from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class Contract(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    request_id: UUID
    professional_id: UUID
    client_id: UUID
    agreed_cents: int
    status: str = "active"
    started_at: datetime
    completed_at: datetime | None = None
