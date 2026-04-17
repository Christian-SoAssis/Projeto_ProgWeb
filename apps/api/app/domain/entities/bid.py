from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class Bid(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    request_id: UUID
    professional_id: UUID
    price_cents: int
    estimated_hours: int | None = None
    message: str | None = None
    status: str = "pending"
    created_at: datetime

    def is_accepted(self) -> bool:
        return self.status == "accepted"

    def is_pending(self) -> bool:
        return self.status == "pending"
