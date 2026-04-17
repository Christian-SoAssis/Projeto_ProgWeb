from dataclasses import dataclass, field
from uuid import UUID
from typing import List, Optional
from datetime import datetime

from app.domain.entities.category import Category

@dataclass
class Professional:
    id: UUID
    user_id: UUID
    bio: str
    document_type: str
    reputation_score: float = 0.0
    is_verified: bool = False
    hourly_rate_cents: Optional[int] = None
    service_radius_km: float = 10.0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    document_path: Optional[str] = None
    
    # Relationships (Entities)
    categories: List[Category] = field(default_factory=list)
    
    # User data (Flattened for domain or nested)
    name: Optional[str] = None # From User
    email: Optional[str] = None # From User
