from datetime import datetime
from typing import List, Optional, Literal
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict, model_validator

# --- Base Schemas ---

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^\+55\d{10,11}$")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()

class ProfessionalBase(BaseModel):
    bio: str = Field(..., min_length=10, max_length=1000)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    service_radius_km: float = Field(..., gt=0, le=200)
    hourly_rate_cents: int = Field(..., gt=0)
    category_ids: List[UUID] = Field(..., min_length=1, max_length=10)
    document_type: Literal["cpf", "cnpj"]

# --- Request Schemas ---

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    consent_terms: bool = Field(...)
    consent_privacy: bool = Field(...)

    @field_validator("consent_terms")
    @classmethod
    def validate_terms(cls, v: bool) -> bool:
        if v is not True:
            raise ValueError("Aceite obrigatório dos termos")
        return v

    @field_validator("consent_privacy")
    @classmethod
    def validate_privacy(cls, v: bool) -> bool:
        if v is not True:
            raise ValueError("Aceite obrigatório da política de privacidade")
        return v

class ProfessionalCreate(ProfessionalBase):
    # ProfessionalCreate is used as a nested model in some flows, 
    # but in POST /professionals it comes as a separate field or multipart.
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^\+55\d{10,11}$")
    avatar_url: Optional[str] = None

class ProfessionalUpdate(BaseModel):
    bio: Optional[str] = Field(None, min_length=10, max_length=1000)
    service_radius_km: Optional[float] = Field(None, gt=0, le=200)
    hourly_rate_cents: Optional[int] = Field(None, gt=0)
    category_ids: Optional[List[UUID]] = Field(None, min_length=1, max_length=10)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()

class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)

class DeleteAccountRequest(BaseModel):
    password: str = Field(..., min_length=1)

# --- Response Schemas ---

class UserResponse(UserBase):
    id: UUID
    role: str
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ProfessionalResponse(ProfessionalBase):
    id: UUID
    user_id: UUID
    is_verified: bool
    reputation_score: float
    rejection_reason: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900 # 15 minutes in seconds
