import pytest
from unittest.mock import MagicMock, AsyncMock
import uuid
from app.application.use_cases.list_categories_use_case import ListCategoriesUseCase
from app.domain.entities.category import Category

@pytest.fixture
def mock_category_repo():
    return MagicMock()

@pytest.fixture
def use_case(mock_category_repo):
    return ListCategoriesUseCase(category_repo=mock_category_repo)

@pytest.mark.asyncio
async def test_list_categories_success(use_case, mock_category_repo):
    # Setup
    categories = [
        Category(id=uuid.uuid4(), name="Cat 1", color="#FF0000"),
        Category(id=uuid.uuid4(), name="Cat 2", color="#00FF00")
    ]
    mock_category_repo.list_active = AsyncMock(return_value=categories)

    # Execute
    result = await use_case.execute()

    # Assert
    assert len(result) == 2
    assert result[0].name == "Cat 1"
    mock_category_repo.list_active.assert_called_once()
