from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ConsentLog(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    user_id: UUID
    consent_type: str # 'terms', 'privacy'
    version: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
