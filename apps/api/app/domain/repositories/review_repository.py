from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Dict, Optional
from app.domain.entities.review import Review

class ReviewRepository(ABC):
    @abstractmethod
    async def save(self, review: Review) -> Review:
        pass

    @abstractmethod
    async def list_by_professional(self, professional_id: UUID) -> List[Review]:
        pass

    @abstractmethod
    async def get_averages(self, professional_id: UUID) -> Dict[str, float]:
        """Returns dict with avg_quality, avg_punctuality, etc."""
        pass
