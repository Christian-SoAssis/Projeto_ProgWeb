from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime
from typing import Optional

@dataclass
class Review:
    id: UUID
    contract_id: UUID
    reviewer_id: UUID
    reviewee_id: UUID
    rating: int
    text: str
    is_authentic: bool = True
    created_at: Optional[datetime] = None
    
    # NLP scores (0.0 - 1.0)
    score_punctuality: Optional[float] = None
    score_quality: Optional[float] = None
    score_cleanliness: Optional[float] = None
    score_communication: Optional[float] = None
