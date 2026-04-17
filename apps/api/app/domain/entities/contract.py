from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum

class ContractStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class Contract:
    id: UUID
    request_id: UUID
    bid_id: UUID
    client_id: UUID
    professional_id: UUID
    amount_cents: int
    status: ContractStatus = ContractStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
