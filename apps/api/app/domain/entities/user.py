from uuid import UUID
from typing import Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict

class UserRole(str, Enum):
    ADMIN = "admin"
    CLIENT = "client"
    PROFESSIONAL = "professional"

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    phone: Optional[str] = None
    password_hash: str
    role: UserRole = UserRole.CLIENT
    is_active: bool = True
    is_verified: bool = False
