import pytest
import uuid
from unittest.mock import AsyncMock
from app.application.use_cases.add_favorite_use_case import AddFavoriteUseCase
from app.application.use_cases.list_favorites_use_case import ListFavoritesUseCase
from app.domain.entities.favorite import Favorite
from app.domain.exceptions import EntityNotFoundError, ConflictError, BusinessRuleViolationError

@pytest.mark.asyncio
async def test_add_favorite_success():
    # Setup
    fav_repo = AsyncMock()
    prof_repo = AsyncMock()
    
    client_id = uuid.uuid4()
    prof_id = uuid.uuid4()
    
    prof_repo.get_by_id.return_value = AsyncMock()
    fav_repo.exists.return_value = False
    fav_repo.save.side_effect = lambda x: x
    
    use_case = AddFavoriteUseCase(fav_repo)
    
    # Execute
    result = await use_case.execute(client_id, prof_id)
    
    # Assert
    assert result.client_id == client_id
    assert result.professional_id == prof_id
    fav_repo.save.assert_called_once()

@pytest.mark.asyncio
async def test_add_favorite_conflict():
    # Setup
    fav_repo = AsyncMock()
    prof_repo = AsyncMock()
    
    prof_repo.get_by_id.return_value = AsyncMock()
    fav_repo.exists.return_value = True # Already favorited
    
    use_case = AddFavoriteUseCase(fav_repo) # Missing prof_repo but it's not used in current implementation?
    # Wait, AddFavoriteUseCase.__init__ takes (self, favorite_repo) only.
    
    # Execute & Assert
    with pytest.raises(BusinessRuleViolationError):
        await use_case.execute(uuid.uuid4(), uuid.uuid4())

@pytest.mark.asyncio
async def test_list_favorites():
    # Setup
    fav_repo = AsyncMock()
    client_id = uuid.uuid4()
    fav_repo.list_by_client.return_value = [Favorite(id=uuid.uuid4(), client_id=client_id, professional_id=uuid.uuid4())]
    
    use_case = ListFavoritesUseCase(fav_repo)
    
    # Execute
    result = await use_case.execute(client_id)
    
    # Assert
    assert len(result) == 1
    fav_repo.list_by_client.assert_called_once_with(client_id)
