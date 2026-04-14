from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ReviewCreate(BaseModel):
    contract_id: UUID
    rating: int = Field(..., ge=1, le=5)
    text: str = Field(..., min_length=10, max_length=2000)


class ReviewResponse(BaseModel):
    id: UUID
    contract_id: UUID
    reviewer_id: UUID
    reviewee_id: UUID
    rating: int
    text: str
    score_punctuality: Optional[float] = None
    score_quality: Optional[float] = None
    score_cleanliness: Optional[float] = None
    score_communication: Optional[float] = None
    is_authentic: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
