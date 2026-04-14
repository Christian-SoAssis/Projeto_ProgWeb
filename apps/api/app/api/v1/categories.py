from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.category import Category

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[dict])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """Lista todas as categorias ativas. Endpoint público."""
    result = await db.execute(
        select(Category)
        .where(Category.is_active == True)
        .order_by(Category.sort_order, Category.name)
    )
    categories = result.scalars().all()
    return [
        {"id": str(cat.id), "name": cat.name, "slug": cat.slug, "color": cat.color}
        for cat in categories
    ]
