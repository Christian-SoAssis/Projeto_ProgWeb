from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator


class RequestImageBase(BaseModel):
    url: str
    content_type: str
    size_bytes: int


class RequestImageResponse(RequestImageBase):
    id: UUID
    analyzed: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RequestBase(BaseModel):
    title: str = Field(..., min_length=5)
    description: Optional[str] = None
    urgency: str = Field(..., pattern="^(immediate|scheduled|flexible)$")
    budget_cents: Optional[int] = Field(None, gt=0)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class RequestCreate(RequestBase):
    category_id: UUID


class RequestUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5)
    description: Optional[str] = None
    urgency: Optional[str] = Field(None, pattern="^(immediate|scheduled|flexible)$")
    budget_cents: Optional[int] = Field(None, gt=0)
    category_id: Optional[UUID] = None


class RequestResponse(RequestBase):
    id: UUID
    client_id: UUID
    category_id: UUID
    status: str
    ai_complexity: Optional[str] = None
    ai_urgency: Optional[str] = None
    ai_specialties: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    images: List[RequestImageResponse] = []

    model_config = ConfigDict(from_attributes=True)
    

