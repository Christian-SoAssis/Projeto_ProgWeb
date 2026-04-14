import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from pydantic import ValidationError

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token
from app.models.user import UserRole
from app.models.professional import Professional
from app.schemas.v1.auth import (
    ProfessionalCreate,
    UserCreate,
    ProfessionalRegisterResponse,
    TokenResponse,
)
from app.schemas.v1.professionals import ProfessionalPublicProfile
from app.services import auth_service

router = APIRouter(prefix="/professionals", tags=["Professionals"])


@router.post("/", response_model=ProfessionalRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_professional(
    request: Request,
    # Multipart fields
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    password: str = Form(...),
    consent_terms: bool = Form(...),
    consent_privacy: bool = Form(...),
    
    # Professional fields
    bio: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    service_radius_km: float = Form(...),
    hourly_rate_cents: int = Form(...),
    category_ids_json: str = Form(..., description="JSON array de UUIDs de categoria"),
    document_type: str = Form(...),
    
    # Upload
    document: UploadFile = File(...),
    
    db: AsyncSession = Depends(get_db)
):
    """Cadastro completo de profissional (Usuário + Profissional + Documento)."""
    
    # Bug 2 fix: guard contra request.client None (testes multipart via httpx)
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "unknown")

    # 1. Validar schemas Pydantic manualmente (desde que vem de Form)
    try:
        category_ids = json.loads(category_ids_json)
        user_in = UserCreate(
            name=name, email=email, phone=phone, password=password,
            consent_terms=consent_terms, consent_privacy=consent_privacy
        )
        prof_in = ProfessionalCreate(
            bio=bio, latitude=latitude, longitude=longitude,
            service_radius_km=service_radius_km, hourly_rate_cents=hourly_rate_cents,
            category_ids=category_ids, document_type=document_type
        )
    except (ValidationError, json.JSONDecodeError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
        
    # 2. Operação Atômica via Services
    try:
        # a) Criar usuário com IP e UA corretos
        user = await auth_service.create_user_with_consent(
            db=db,
            user_in=user_in,
            role=UserRole.PROFESSIONAL,
            ip_address=ip,
            user_agent=ua,
        )
        
        # b) Criar perfil profissional e salvar documento
        professional = await auth_service.build_professional(
            db=db, user_id=user.id, prof_in=prof_in, document=document
        )
        
        await db.commit()
        await db.refresh(professional)

        # Montar resposta manualmente para incluir role do user
        # e evitar serialização de campos que não existem na tabela (category_ids)
        return ProfessionalRegisterResponse.from_professional(professional, user)
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"\n🔴 ERRO INTERNO PROFISSIONAL: {type(e).__name__}: {e}")
        print(traceback.format_exc())
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno no cadastro: {type(e).__name__}: {e}"
        )


@router.get("/{professional_id}", response_model=ProfessionalPublicProfile)
async def get_professional_profile(
    professional_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retorna o perfil público de um profissional por ID."""
    query = (
        select(Professional)
        .options(
            joinedload(Professional.user),
            joinedload(Professional.categories)
        )
        .where(Professional.id == professional_id)
    )
    
    result = await db.execute(query)
    professional = result.scalar_one_or_none()
    
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profissional não encontrado"
        )
    
    # Formatar resposta para bater com o schema ProfessionalPublicProfile
    return {
        "id": professional.id,
        "name": professional.user.name,
        "bio": professional.bio,
        "reputation_score": professional.reputation_score,
        "is_verified": professional.is_verified,
        "hourly_rate_cents": professional.hourly_rate_cents,
        "categories": [
            {"id": cat.id, "name": cat.name, "color": cat.color}
            for cat in professional.categories
        ]
    }
