from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.category import Category
from app.schemas.v1.categories import CategoryResponse

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("", response_model=List[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """
    Retorna a lista de todas as categorias ativas, ordenadas por ordem de exibição.
    """
    stmt = (
        select(Category)
        .where(Category.is_active == True)
        .order_by(Category.sort_order.asc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()
