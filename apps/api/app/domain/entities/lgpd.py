from uuid import UUID
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field

@dataclass
class ConsentLog:
    user_id: UUID
    consent_type: str # 'terms', 'privacy'
    version: str
    is_granted: bool
    id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
