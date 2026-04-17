from typing import List
from fastapi import APIRouter, Depends

from app.api.v1.deps import get_list_categories_use_case
from app.application.use_cases.list_categories_use_case import ListCategoriesUseCase

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("", response_model=List[dict])
async def list_categories(
    list_use_case: ListCategoriesUseCase = Depends(get_list_categories_use_case)
):
    """Lista todas as categorias ativas via Use Case."""
    categories = await list_use_case.execute()
    return [
        {"id": str(cat.id), "name": cat.name, "color": cat.color}
        for cat in categories
    ]
