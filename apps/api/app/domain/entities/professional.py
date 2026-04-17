from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class Category(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    color: Optional[str] = None

class Professional(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    bio: str
    reputation_score: float = 0.0
    is_verified: bool = False
    hourly_rate_cents: Optional[int] = None
    service_radius_km: float = 10.0
    
    # Relationships (Entities)
    categories: List[Category] = []
    
    # User data (Flattened for domain or nested)
    name: Optional[str] = None # From User
    email: Optional[str] = None # From User
