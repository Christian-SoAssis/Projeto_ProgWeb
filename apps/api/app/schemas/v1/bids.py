from uuid import UUID
from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class BidCreate(BaseModel):
    request_id: UUID
    price_cents: int = Field(..., gt=0)
    estimated_hours: Optional[int] = Field(None, gt=0)
    message: Optional[str] = Field(None, max_length=500)


class BidUpdate(BaseModel):
    status: Literal["accepted", "rejected"]


class BidResponse(BaseModel):
    id: UUID
    request_id: UUID
    professional_id: UUID
    price_cents: int
    estimated_hours: Optional[int] = None
    message: Optional[str] = None
    status: Literal["pending", "accepted", "rejected", "cancelled"]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContractResponse(BaseModel):
    id: UUID
    request_id: UUID
    professional_id: UUID
    client_id: UUID
    agreed_cents: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class BidAcceptResponse(BaseModel):
    """Retorno ao aceitar um bid — inclui bid atualizado + contrato criado."""
    bid: BidResponse
    contract: Optional[ContractResponse] = None


class BidRejectResponse(BaseModel):
    """Retorno ao rejeitar um bid."""
    bid: BidResponse
    contract: None = None
