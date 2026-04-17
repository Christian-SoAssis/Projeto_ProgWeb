from typing import List
from app.domain.entities.category import Category
from app.domain.repositories.category_repository import CategoryRepository

class ListCategoriesUseCase:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    async def execute(self) -> List[Category]:
        return await self.category_repo.list_active()
