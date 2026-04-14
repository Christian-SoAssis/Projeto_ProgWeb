from uuid import UUID
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class FavoriteCreate(BaseModel):
    professional_id: UUID


class FavoriteResponse(BaseModel):
    id: UUID
    professional_id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class NotificationResponse(BaseModel):
    id: UUID
    type: str
    payload: dict
    read_at: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class NotificationMarkRead(BaseModel):
    notification_ids: List[UUID] = Field(..., min_length=1, max_length=100)


class ProfessionalMetrics(BaseModel):
    total_earnings_cents: int
    completed_jobs: int
    pending_bids: int
    reputation_score: float
    conversion_rate: float  # contratos / bids recebidos


class ProfessionalUpdateRequest(BaseModel):
    bio: Optional[str] = Field(None, min_length=10, max_length=1000)
    service_radius_km: Optional[float] = Field(None, gt=0, le=200)
    hourly_rate_cents: Optional[int] = Field(None, gt=0)


class SearchProfessionalResponse(BaseModel):
    id: UUID
    user_id: UUID
    bio: str
    latitude: float
    longitude: float
    service_radius_km: float
    hourly_rate_cents: Optional[int] = None
    reputation_score: float
    is_verified: bool
    distance_km: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)
