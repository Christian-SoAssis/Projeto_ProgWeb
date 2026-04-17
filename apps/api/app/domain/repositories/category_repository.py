from abc import ABC, abstractmethod
from typing import List
from app.domain.entities.professional import Category

class CategoryRepository(ABC):
    @abstractmethod
    async def list_active(self) -> List[Category]:
        pass
