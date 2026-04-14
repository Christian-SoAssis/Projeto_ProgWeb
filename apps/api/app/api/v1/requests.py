from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.request import Request
from app.schemas.v1.requests import RequestCreate, RequestResponse
from app.schemas.v1.matching import MatchResponse
from app.services.request_service import request_service
from app.services.matching_service import get_matches
from app.core.config import settings
from app.models.bid import Bid
from app.schemas.v1.bids import BidResponse as BidResp

router = APIRouter(prefix="/requests", tags=["Requests"])

@router.post("", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
    title: str = Form(..., min_length=5),
    description: Optional[str] = Form(None),
    category_id: uuid.UUID = Form(...),
    urgency: str = Form(..., pattern="^(immediate|scheduled|flexible)$"),
    latitude: float = Form(..., ge=-90, le=90),
    longitude: float = Form(..., ge=-180, le=180),
    budget_cents: Optional[int] = Form(None, gt=0),
    images: List[UploadFile] = File([]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo pedido de serviço com suporte a múltiplas imagens e geolocalização.
    Dispara automaticamente a análise de IA (Gemini Vision) em segundo plano.
    """
    if len(images) > 5:
        raise HTTPException(status_code=400, detail="Máximo de 5 imagens permitido.")

    # Validar tipos de arquivo e tamanho
    for img in images:
        if img.content_type not in ["image/jpeg", "image/png", "image/webp"]:
            raise HTTPException(status_code=400, detail=f"Tipo de arquivo inválido: {img.content_type}")
        # Note: Tamanho real é validado no salvamento ou via middleware se houver

    request_data = RequestCreate(
        title=title,
        description=description,
        category_id=category_id,
        urgency=urgency,
        latitude=latitude,
        longitude=longitude,
        budget_cents=budget_cents
    )

    return await request_service.create_request(db, current_user.id, request_data, images)


@router.get("", response_model=List[RequestResponse])
async def list_requests(
    client_only: bool = Query(False),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista pedidos sugeridos (para profissionais) ou pedidos do próprio cliente (se client_only=True).
    """
    client_id = current_user.id if client_only else None
    return await request_service.list_requests(db, client_id=client_id, limit=limit, offset=offset)


@router.get("/{request_id}", response_model=RequestResponse)
async def get_request(
    request_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna os detalhes de um pedido específico, incluindo o status da análise de IA.
    """
    request = await request_service.get_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    return request


@router.get("/{request_id}/matches", response_model=List[MatchResponse])
async def get_request_matches(
    request_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna top-10 profissionais rankeados para o pedido.
    Apenas o cliente dono do pedido pode acessar.
    """
    # 1. Buscar o request com location carregada do banco
    result = await db.execute(
        select(Request)
        .where(Request.id == request_id)
        .execution_options(populate_existing=True)
    )
    request = result.scalar_one_or_none()

    if not request:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # 2. Verificar ownership
    if str(request.client_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Acesso negado")

    # 3. Executar matching
    matches = await get_matches(db, request)
    return matches


@router.get("/{request_id}/bids", response_model=List[BidResp])
async def list_bids_for_request(
    request_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista bids de um pedido. Apenas o cliente dono do pedido pode ver."""
    result = await db.execute(
        select(Request).where(Request.id == request_id)
    )
    request = result.scalar_one_or_none()

    if not request:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if str(request.client_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Acesso negado")

    result = await db.execute(
        select(Bid)
        .where(Bid.request_id == request_id)
        .order_by(Bid.created_at.desc())
    )
    return result.scalars().all()
