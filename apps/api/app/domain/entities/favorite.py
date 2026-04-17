from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import Optional

@dataclass
class Favorite:
    id: UUID
    client_id: UUID
    professional_id: UUID
    created_at: Optional[datetime] = None
