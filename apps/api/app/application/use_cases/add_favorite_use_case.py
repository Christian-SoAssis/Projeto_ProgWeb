import uuid
from dataclasses import dataclass
from app.domain.entities.favorite import Favorite
from app.domain.repositories.favorite_repository import FavoriteRepository
from app.domain.exceptions import BusinessRuleViolationError

class AddFavoriteUseCase:
    def __init__(self, favorite_repo: FavoriteRepository):
        self.favorite_repo = favorite_repo

    async def execute(self, client_id: uuid.UUID, professional_id: uuid.UUID) -> Favorite:
        if await self.favorite_repo.exists(client_id, professional_id):
            raise BusinessRuleViolationError("Profissional já está nos favoritos")
        
        favorite = Favorite(
            id=uuid.uuid4(),
            client_id=client_id,
            professional_id=professional_id
        )
        return await self.favorite_repo.save(favorite)
