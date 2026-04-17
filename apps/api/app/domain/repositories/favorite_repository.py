from abc import ABC, abstractmethod
from uuid import UUID
from typing import List
from app.domain.entities.favorite import Favorite

class FavoriteRepository(ABC):
    @abstractmethod
    async def save(self, favorite: Favorite) -> Favorite:
        pass

    @abstractmethod
    async def list_by_client(self, client_id: UUID) -> List[Favorite]:
        pass

    @abstractmethod
    async def delete(self, client_id: UUID, professional_id: UUID) -> None:
        pass

    @abstractmethod
    async def exists(self, client_id: UUID, professional_id: UUID) -> bool:
        pass
