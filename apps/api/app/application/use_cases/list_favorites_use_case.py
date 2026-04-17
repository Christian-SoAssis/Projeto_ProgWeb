import uuid
from typing import List
from app.domain.entities.favorite import Favorite
from app.domain.repositories.favorite_repository import FavoriteRepository

class ListFavoritesUseCase:
    def __init__(self, favorite_repo: FavoriteRepository):
        self.favorite_repo = favorite_repo

    async def execute(self, client_id: uuid.UUID) -> List[Favorite]:
        return await self.favorite_repo.list_by_client(client_id)
