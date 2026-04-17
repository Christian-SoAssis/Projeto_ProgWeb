from abc import ABC, abstractmethod
from typing import List
from app.domain.entities.lgpd import ConsentLog

class ConsentRepository(ABC):
    @abstractmethod
    async def save_all(self, consents: List[ConsentLog]) -> None:
        pass
