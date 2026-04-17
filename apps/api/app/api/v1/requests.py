from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.request import Request
from app.api.v1.deps import get_create_request_use_case, get_request_use_case, get_list_requests_use_case
from app.application.use_cases.create_request_use_case import CreateRequestUseCase, CreateRequestInput
from app.application.use_cases.get_request_use_case import GetRequestUseCase
from app.application.use_cases.list_requests_use_case import ListRequestsUseCase
from app.domain.exceptions import EntityNotFoundError, UnauthorizedError, DomainError
from app.schemas.v1.requests import RequestResponse
from app.schemas.v1.matching import MatchResponse
from app.schemas.v1.bids import BidResponse as BidResp
from app.models.bid import Bid
from app.services.matching_service import get_matches

router = APIRouter(prefix="/requests", tags=["Requests"])

@router.post("", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request_endpoint(
    title: str = Form(..., min_length=5),
    description: Optional[str] = Form(None),
    category_id: uuid.UUID = Form(...),
    urgency: str = Form(..., pattern="^(immediate|scheduled|flexible)$"),
    latitude: float = Form(..., ge=-90, le=90),
    longitude: float = Form(..., ge=-180, le=180),
    budget_cents: Optional[int] = Form(None, gt=0),
    images: List[UploadFile] = File([]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    use_case: CreateRequestUseCase = Depends(get_create_request_use_case),
):
    """
    Cria um novo pedido de serviço com suporte a múltiplas imagens e geolocalização.
    Dispara automaticamente a análise de IA (Gemini Vision) em segundo plano.
    """
    if len(images) > 5:
        raise HTTPException(status_code=400, detail="Máximo de 5 imagens permitido.")

    for img in images:
        if img.content_type not in ["image/jpeg", "image/png", "image/webp"]:
            raise HTTPException(status_code=400, detail=f"Tipo de arquivo inválido: {img.content_type}")

    request_input = CreateRequestInput(
        client_id=current_user.id,
        category_id=category_id,
        title=title,
        description=description,
        latitude=latitude,
        longitude=longitude,
        urgency=urgency,
        budget_cents=budget_cents,
        images=images
    )

    try:
        request = await use_case.execute(request_input)
        await db.commit()
        return request
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[RequestResponse])
async def list_requests_endpoint(
    client_only: bool = Query(False),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    use_case: ListRequestsUseCase = Depends(get_list_requests_use_case),
):
    """
    Lista pedidos sugeridos (para profissionais) ou pedidos do próprio cliente (se client_only=True).
    """
    client_id = current_user.id if client_only else None
    return await use_case.execute(client_id=client_id, limit=limit, offset=offset)


@router.get("/{request_id}", response_model=RequestResponse)
async def get_request_endpoint(
    request_id: uuid.UUID,
    use_case: GetRequestUseCase = Depends(get_request_use_case),
):
    """
    Retorna os detalhes de um pedido específico, incluindo o status da análise de IA.
    """
    try:
        return await use_case.execute(request_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{request_id}/matches", response_model=List[MatchResponse])
async def get_request_matches(
    request_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    get_use_case: GetRequestUseCase = Depends(get_request_use_case),
):
    """
    Retorna top-10 profissionais rankeados para o pedido.
    Apenas o cliente dono do pedido pode acessar.
    """
    try:
        request_entity = await get_use_case.execute(request_id)
        if request_entity.client_id != current_user.id:
            raise HTTPException(status_code=403, detail="Acesso negado")

        # Matching service ainda não foi refatorado, mas usamos o modelo do banco dele por enquanto
        # ou transformamos a entidade de volta para modelo se necessário.
        # Para evitar re-query, podemos usar o request_repo se ele retornar o modelo SQLAlchemy.
        # Mas em Clean Architecture, o Matching Service deveria aceitar a Entidade.
        # Como estamos refatorando aos poucos, vamos buscar o modelo aqui.
        result = await db.execute(
            select(Request).where(Request.id == request_id)
        )
        request_model = result.scalar_one()
        matches = await get_matches(db, request_model)
        return matches
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{request_id}/bids", response_model=List[BidResp])
async def list_bids_for_request(
    request_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    get_use_case: GetRequestUseCase = Depends(get_request_use_case),
):
    """Lista bids de um pedido. Apenas o cliente dono do pedido pode ver."""
    try:
        request = await get_use_case.execute(request_id)
        if request.client_id != current_user.id:
            raise HTTPException(status_code=403, detail="Acesso negado")

        result = await db.execute(
            select(Bid)
            .where(Bid.request_id == request_id)
            .order_by(Bid.created_at.desc())
        )
        return result.scalars().all()
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
