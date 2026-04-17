from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum

class BidStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"

@dataclass
class Bid:
    id: UUID
    request_id: UUID
    professional_id: UUID
    price_cents: int
    message: str
    status: BidStatus = BidStatus.PENDING
    created_at: Optional[datetime] = None
    professional_name: Optional[str] = None
    professional_avatar: Optional[str] = None

    def is_accepted(self) -> bool:
        return self.status == BidStatus.ACCEPTED

    def is_pending(self) -> bool:
        return self.status == "pending"
