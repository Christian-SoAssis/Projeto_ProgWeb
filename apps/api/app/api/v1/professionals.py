"""Router de profissionais — POST /professionals, PATCH /admin/professionals/:id."""
import os
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.professional import Professional
from app.models.user import User, UserRole
from app.schemas.v1.professionals import (
    ProfessionalApproval,
    ProfessionalCreate,
    ProfessionalResponse,
)
from app.core.config import settings

router = APIRouter(tags=["Profissionais"])


@router.post(
    "/professionals",
    response_model=ProfessionalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar profissional com upload de documento",
)
async def create_professional(
    bio: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    service_radius_km: float = Form(...),
    hourly_rate_cents: int = Form(...),
    category_ids: str = Form(...),  # JSON string: '["uuid1","uuid2"]'
    document_type: str = Form(...),
    document: UploadFile = File(...),
    user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> ProfessionalResponse:
    """
    Cadastra profissional para o usuário autenticado.
    - Aceita multipart/form-data com documento (CPF/CNPJ)
    - Salva arquivo em ./uploads/docs/<user_id>/
    - Muda role do usuário para professional
    """
    import json

    # Validar com Pydantic
    try:
        ids = json.loads(category_ids)
        payload = ProfessionalCreate(
            bio=bio,
            latitude=latitude,
            longitude=longitude,
            service_radius_km=service_radius_km,
            hourly_rate_cents=hourly_rate_cents,
            category_ids=ids,
            document_type=document_type,
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Verificar se já tem perfil
    existing = await db.execute(
        select(Professional).where(Professional.user_id == user.id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Profissional já cadastrado")

    # Salvar documento
    docs_dir = os.path.join(settings.UPLOADS_DIR, "docs", str(user.id))
    os.makedirs(docs_dir, exist_ok=True)
    doc_ext = os.path.splitext(document.filename or "doc")[1] or ".pdf"
    doc_path = os.path.join(docs_dir, f"document{doc_ext}")
    with open(doc_path, "wb") as f:
        content = await document.read()
        f.write(content)

    # Criar profissional
    professional = Professional(
        id=uuid.uuid4(),
        user_id=user.id,
        bio=payload.bio,
        latitude=payload.latitude,
        longitude=payload.longitude,
        service_radius_km=payload.service_radius_km,
        hourly_rate_cents=payload.hourly_rate_cents,
        document_type=payload.document_type,
        document_path=doc_path,
    )
    db.add(professional)

    # Mudar role para professional
    user.role = UserRole.PROFESSIONAL
    await db.commit()
    await db.refresh(professional)

    return ProfessionalResponse.model_validate(professional)


@router.patch(
    "/admin/professionals/{professional_id}",
    response_model=ProfessionalResponse,
    summary="Aprovar/rejeitar profissional (admin)",
)
async def approve_professional(
    professional_id: uuid.UUID,
    body: ProfessionalApproval,
    _admin: Annotated[User, Depends(require_role("admin"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProfessionalResponse:
    """Admin aprova ou rejeita o cadastro de um profissional."""
    result = await db.execute(
        select(Professional).where(Professional.id == professional_id)
    )
    prof = result.scalar_one_or_none()
    if not prof:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")

    prof.is_verified = body.is_verified
    prof.rejection_reason = body.rejection_reason
    await db.commit()
    await db.refresh(prof)

    return ProfessionalResponse.model_validate(prof)
