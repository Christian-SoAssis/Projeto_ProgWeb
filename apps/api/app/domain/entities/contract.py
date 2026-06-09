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
    client_id: UUID
    professional_id: UUID
    agreed_cents: int
    status: ContractStatus = ContractStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None

    @property
    def started_at(self) -> Optional[datetime]:
        return self.created_at

    @property
    def completed_at(self) -> Optional[datetime]:
        return self.updated_at
