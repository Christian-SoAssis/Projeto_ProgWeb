from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from app.domain.entities.contract import Contract

class ContractRepository(ABC):
    @abstractmethod
    async def save(self, contract: Contract) -> Contract:
        pass

    @abstractmethod
    async def count_completed_by_professional(self, professional_id: UUID) -> int:
        pass

    @abstractmethod
    async def get_by_id(self, contract_id: UUID) -> Optional[Contract]:
        pass
