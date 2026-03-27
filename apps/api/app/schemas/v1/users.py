from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, pattern=r"^\+55\d{10,11}$")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    consent_terms: bool = Field(...)
    consent_privacy: bool = Field(...)

    @field_validator("consent_terms", "consent_privacy")
    @classmethod
    def must_accept(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Aceite obrigatório dos termos")
        return v


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    phone: Optional[str]
    role: Literal["client", "professional", "admin"]
    avatar_url: Optional[str]
    is_active: bool
    last_login_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}
