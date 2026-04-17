import uuid
from app.domain.repositories.favorite_repository import FavoriteRepository
from app.domain.exceptions import EntityNotFoundError

class RemoveFavoriteUseCase:
    def __init__(self, favorite_repo: FavoriteRepository):
        self.favorite_repo = favorite_repo

    async def execute(self, client_id: uuid.UUID, professional_id: uuid.UUID) -> None:
        if not await self.favorite_repo.exists(client_id, professional_id):
            raise EntityNotFoundError("Favorito não encontrado")
        await self.favorite_repo.delete(client_id, professional_id)
