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


class ContractDisputeCreate(BaseModel):
    reason: str = Field(..., min_length=10, max_length=500)
    category: str = Field(..., pattern="^(quality|no_show|overcharge|damage|other)$")
    evidence_urls: Optional[List[str]] = Field(default_factory=list)


class DisputeResponseCreate(BaseModel):
    message: str = Field(..., min_length=10, max_length=1000)
    evidence_urls: Optional[List[str]] = Field(default_factory=list)
    proposed_resolution: str = Field(..., min_length=10, max_length=500)


class DisputeResolve(BaseModel):
    resolution: str = Field(..., pattern="^(refund_full|refund_partial|refund_denied)$")
    refund_percent: Optional[int] = Field(None, ge=1, le=99)
    admin_notes: str = Field(..., min_length=5, max_length=1000)


class DisputeResponse(BaseModel):
    id: UUID
    payment_id: Optional[UUID] = None
    contract_id: UUID
    opened_by_user_id: UUID
    reason: str
    category: str
    evidence_urls: List[str] = Field(default_factory=list)
    status: str
    resolution: Optional[str] = None
    refund_percent: Optional[int] = None
    admin_notes: Optional[str] = None
    response_message: Optional[str] = None
    response_evidence_urls: Optional[List[str]] = Field(default_factory=list)
    proposed_resolution: Optional[str] = None
    response_deadline: datetime
    responded_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

