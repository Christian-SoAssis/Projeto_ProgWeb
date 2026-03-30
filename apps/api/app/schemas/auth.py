from datetime import datetime
from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# Mock CategoryResponse as we don't know if categories is fully modeled yet
class CategoryResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    model_config = {"from_attributes": True}


# --- Consent ---
class ConsentPayload(BaseModel):
    consent_terms: bool
    consent_privacy: bool

    @field_validator("consent_terms", "consent_privacy")
    @classmethod
    def check_consent(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Aceite obrigatório dos termos")
        return value

class ConsentResponse(BaseModel):
    consent_type: str
    version: str
    accepted_at: datetime
    model_config = {"from_attributes": True}


# --- User ---
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, pattern=r"^\+55\d{10,11}$")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    consent_terms: bool
    consent_privacy: bool

    @field_validator("email", mode="before")
    @classmethod
    def normalizer_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.lower()
        return v

    @field_validator("consent_terms", "consent_privacy")
    @classmethod
    def check_consent(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Aceite obrigatório dos termos")
        return value

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^\+55\d{10,11}$")

class UserResponse(UserBase):
    id: UUID
    role: str
    is_active: bool
    avatar_url: Optional[str] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# --- Professional ---
class ProfessionalBase(BaseModel):
    bio: Optional[str] = Field(None, max_length=1000)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    service_radius_km: float = Field(..., gt=0, le=200)
    hourly_rate_cents: Optional[int] = Field(None, gt=0)

class ProfessionalCreate(UserCreate, ProfessionalBase):
    category_ids: list[UUID] = Field(..., min_length=1, max_length=10)
    document_type: Literal["cpf", "cnpj"]

class ProfessionalUpdate(BaseModel):
    bio: Optional[str] = Field(None, max_length=1000)
    service_radius_km: Optional[float] = Field(None, gt=0, le=200)
    hourly_rate_cents: Optional[int] = Field(None, gt=0)
    category_ids: Optional[list[UUID]] = Field(None, min_length=1, max_length=10)

class ProfessionalResponse(UserResponse, ProfessionalBase):
    is_verified: bool
    reputation_score: float
    categories: list[CategoryResponse]
    verified_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# --- Requests auxiliares ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    model_config = {"from_attributes": True}

class DeleteAccountRequest(BaseModel):
    password: str = Field(..., min_length=1)
