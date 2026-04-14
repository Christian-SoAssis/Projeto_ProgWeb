"""Schemas Pydantic v2 para Profissional."""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProfessionalCreate(BaseModel):
    """Cadastro de profissional (enviado junto com documentos via multipart)."""
    bio: str = Field(..., min_length=10, max_length=1000)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    service_radius_km: float = Field(..., gt=0, le=200)
    hourly_rate_cents: int = Field(..., gt=0)
    category_ids: list[UUID] = Field(..., min_length=1, max_length=10)
    document_type: str = Field(..., pattern=r"^(cpf|cnpj)$")


class ProfessionalResponse(BaseModel):
    id: UUID
    user_id: UUID
    bio: str
    service_radius_km: float
    hourly_rate_cents: int
    reputation_score: float
    is_verified: bool

    model_config = {"from_attributes": True}


class ProfessionalApproval(BaseModel):
    """Payload do admin para aprovar/rejeitar profissional."""
    is_verified: bool
    rejection_reason: Optional[str] = Field(None, max_length=500)


class CategoryBasic(BaseModel):
    """Schema básico de categoria para exibição em perfis."""
    id: UUID
    name: str
    color: Optional[str] = None

    model_config = {"from_attributes": True}


class ProfessionalPublicProfile(BaseModel):
    """Perfil público do profissional para clientes."""
    id: UUID
    name: str
    bio: str
    reputation_score: float
    is_verified: bool
    hourly_rate_cents: Optional[int]
    categories: list[CategoryBasic]

    model_config = {"from_attributes": True}
