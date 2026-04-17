from dataclasses import dataclass
from uuid import UUID
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    CLIENT = "client"
    PROFESSIONAL = "professional"
    ADMIN = "admin"

@dataclass
class User:
    id: UUID
    name: str
    email: str
    password_hash: str
    role: UserRole
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
