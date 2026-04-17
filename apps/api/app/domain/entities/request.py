from datetime import datetime
from dataclasses import dataclass, field
from uuid import UUID
from typing import List, Optional
from enum import Enum

class RequestStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class RequestImage:
    id: UUID
    request_id: UUID
    url: str
    content_type: str
    size_bytes: int
    created_at: datetime
    analyzed: bool = False

@dataclass
class Request:
    id: UUID
    client_id: UUID
    category_id: UUID
    title: str
    latitude: float
    longitude: float
    urgency: str
    created_at: datetime
    updated_at: datetime
    description: Optional[str] = None
    budget_cents: Optional[int] = None
    status: RequestStatus = RequestStatus.OPEN
    ai_complexity: Optional[str] = None
    ai_urgency: Optional[str] = None
    ai_specialties: Optional[List[str]] = None
    images: List[RequestImage] = field(default_factory=list)
    category_name: Optional[str] = None
    client_name: Optional[str] = None

    def can_accept_bids(self) -> bool:
        return self.status == "open"
    
    def is_matched(self) -> bool:
        return self.status == "matched"
