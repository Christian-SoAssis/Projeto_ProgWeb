from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List
from app.domain.entities.request import Request

class RequestRepository(ABC):
    @abstractmethod
    async def get_by_id(self, request_id: UUID) -> Optional[Request]:
        pass

    @abstractmethod
    async def list(self, client_id: Optional[UUID] = None, limit: int = 20, offset: int = 0) -> List[Request]:
        pass

    @abstractmethod
    async def save(self, request: Request) -> Request:
        pass

    @abstractmethod
    async def update(self, request: Request) -> Request:
        pass
