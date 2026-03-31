"""Schemas Pydantic v2 para autenticação (register, login, refresh, tokens)."""
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


from app.models.user import UserRole


class RegisterRequest(BaseModel):
    """Cadastro de cliente."""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, pattern=r"^\+55\d{10,11}$")
    password: str = Field(..., min_length=8, max_length=128)
    consent_terms: bool = Field(...)
    consent_privacy: bool = Field(...)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()

    @field_validator("consent_terms", "consent_privacy")
    @classmethod
    def must_accept(cls, v: bool, info) -> bool:
        if not v:
            raise ValueError(f"Aceite obrigatório de {info.field_name}")
        return v


class LoginRequest(BaseModel):
    """Credenciais de login."""
    email: EmailStr
    password: str = Field(..., min_length=1)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()


class RefreshRequest(BaseModel):
    """Requisição de rotação de refresh token."""
    refresh_token: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Par de tokens retornado após login/refresh."""
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


class MeResponse(BaseModel):
    """Perfil do usuário autenticado."""
    id: UUID
    name: str
    email: EmailStr
    phone: Optional[str]
    role: UserRole
    avatar_url: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}


class DeleteAccountRequest(BaseModel):
    """Confirmação de senha para exclusão de conta (LGPD)."""
    password: str = Field(..., min_length=1)


class ConsentResponse(BaseModel):
    """Log de consentimento aceito."""
    consent_type: str
    version: str
    accepted_at: datetime

    model_config = {"from_attributes": True}
