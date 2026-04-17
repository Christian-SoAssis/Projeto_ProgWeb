import uuid
from typing import List, Optional
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.favorite import Favorite as FavoriteEntity
from app.domain.repositories.favorite_repository import FavoriteRepository
from app.models.favorite import Favorite as FavoriteModel
from app.infrastructure.database.mappers import FavoriteMapper

class FavoriteRepositoryImpl(FavoriteRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, favorite: FavoriteEntity) -> FavoriteEntity:
        model = FavoriteMapper.to_model(favorite)
        self.db.add(model)
        await self.db.flush()
        return FavoriteMapper.to_entity(model)

    async def list_by_client(self, client_id: uuid.UUID) -> List[FavoriteEntity]:
        result = await self.db.execute(
            select(FavoriteModel)
            .where(FavoriteModel.client_id == client_id)
            .order_by(FavoriteModel.created_at.desc())
        )
        return [FavoriteMapper.to_entity(row) for row in result.scalars().all()]

    async def delete(self, client_id: uuid.UUID, professional_id: uuid.UUID) -> None:
        await self.db.execute(
            delete(FavoriteModel).where(
                FavoriteModel.client_id == client_id,
                FavoriteModel.professional_id == professional_id
            )
        )
        await self.db.flush()

    async def exists(self, client_id: uuid.UUID, professional_id: uuid.UUID) -> bool:
        result = await self.db.execute(
            select(func.count(FavoriteModel.id))
            .where(
                FavoriteModel.client_id == client_id,
                FavoriteModel.professional_id == professional_id
            )
        )
        return result.scalar() > 0
