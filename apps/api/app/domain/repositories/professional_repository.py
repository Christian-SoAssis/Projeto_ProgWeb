from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List
from app.domain.entities.professional import Professional

class ProfessionalRepository(ABC):
    @abstractmethod
    async def get_by_id(self, professional_id: UUID) -> Optional[Professional]:
        pass

    @abstractmethod
    async def list_available(self, category_id: Optional[UUID] = None) -> List[Professional]:
        pass

    @abstractmethod
    async def save(self, professional: Professional) -> Professional:
        pass
