from datetime import datetime
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class RequestImage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    request_id: UUID
    url: str
    content_type: str
    size_bytes: int
    analyzed: bool = False
    created_at: datetime

class Request(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    client_id: UUID
    category_id: UUID
    title: str = Field(min_length=5)
    description: Optional[str] = None
    latitude: float
    longitude: float
    urgency: str
    budget_cents: Optional[int] = None
    status: str = "open"
    
    # AI Fields
    ai_complexity: Optional[str] = None
    ai_urgency: Optional[str] = None
    ai_specialties: Optional[List[str]] = None
    
    created_at: datetime
    updated_at: datetime
    
    images: List[RequestImage] = []

    def can_accept_bids(self) -> bool:
        return self.status == "open"
    
    def is_matched(self) -> bool:
        return self.status == "matched"
