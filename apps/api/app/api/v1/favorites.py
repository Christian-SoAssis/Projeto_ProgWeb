import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.favorite import Favorite
from app.schemas.v1.panels import FavoriteCreate, FavoriteResponse

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.post("", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    fav_in: FavoriteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fav = Favorite(
        client_id=current_user.id,
        professional_id=fav_in.professional_id,
    )
    db.add(fav)
    try:
        await db.flush()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profissional já está nos favoritos"
        )
    await db.commit()
    await db.refresh(fav)
    return fav


@router.get("", response_model=List[FavoriteResponse])
async def list_favorites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Favorite)
        .where(Favorite.client_id == current_user.id)
        .order_by(Favorite.created_at.desc())
    )
    return result.scalars().all()


@router.delete("/{professional_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    professional_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Favorite).where(
            Favorite.client_id == current_user.id,
            Favorite.professional_id == professional_id,
        )
    )
    fav = result.scalar_one_or_none()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorito não encontrado")
    await db.delete(fav)
    await db.commit()
