from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.professional import Category as DomainCategory
from app.domain.repositories.category_repository import CategoryRepository
from app.models.category import Category as CategoryModel

class CategoryRepositoryImpl(CategoryRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_active(self) -> List[DomainCategory]:
        query = (
            select(CategoryModel)
            .where(CategoryModel.is_active == True)
            .order_by(CategoryModel.sort_order, CategoryModel.name)
        )
        result = await self.db.execute(query)
        models = result.scalars().all()
        return [
            DomainCategory(id=m.id, name=m.name, color=m.color)
            for m in models
        ]
