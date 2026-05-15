from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class PaymentResponse(BaseModel):
    id: UUID
    contract_id: UUID
    amount_cents: int
    fee_cents: int
    professional_amount_cents: int
    status: str
    mp_preference_id: Optional[str] = None
    mp_payment_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentIntentCreate(BaseModel):
    contract_id: UUID


class WebhookPayload(BaseModel):
    action: str
    api_version: str
    data: Dict[str, Any]
    date_created: datetime
    id: str
    live_mode: bool
    type: str
    user_id: str


class DisputeCreate(BaseModel):
    payment_id: UUID
    reason: str = Field(..., min_length=10, max_length=500)
    category: str = Field(..., pattern="^(quality|no_show|overcharge|damage|other)$")


class DisputeResponse(BaseModel):
    id: UUID
    payment_id: UUID
    opened_by_user_id: UUID
    reason: str
    category: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
