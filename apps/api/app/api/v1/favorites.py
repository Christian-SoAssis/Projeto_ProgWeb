import uuid
from typing import List
from fastapi import APIRouter, Depends, status

from app.api.v1.deps import (
    get_add_favorite_use_case,
    get_list_favorites_use_case,
    get_remove_favorite_use_case
)
from app.core.dependencies import get_current_user
from app.domain.entities.user import User
from app.schemas.v1.panels import FavoriteCreate, FavoriteResponse

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.post("", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    fav_in: FavoriteCreate,
    use_case = Depends(get_add_favorite_use_case),
    current_user: User = Depends(get_current_user),
):
    """Adiciona um profissional aos favoritos do cliente."""
    return await use_case.execute(
        client_id=current_user.id,
        professional_id=fav_in.professional_id
    )


@router.get("", response_model=List[FavoriteResponse])
async def list_favorites(
    use_case = Depends(get_list_favorites_use_case),
    current_user: User = Depends(get_current_user),
):
    """Lista os profissionais favoritos do cliente."""
    return await use_case.execute(client_id=current_user.id)


@router.delete("/{professional_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    professional_id: uuid.UUID,
    use_case = Depends(get_remove_favorite_use_case),
    current_user: User = Depends(get_current_user),
):
    """Remove um profissional dos favoritos do cliente."""
    await use_case.execute(
        client_id=current_user.id,
        professional_id=professional_id
    )
