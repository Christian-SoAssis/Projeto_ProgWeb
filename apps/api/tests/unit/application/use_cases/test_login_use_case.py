import pytest
import uuid
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.login_use_case import LoginUseCase, LoginInput
from app.domain.entities.user import User, UserRole
from app.domain.exceptions import UnauthorizedError
from app.core.security import hash_password

@pytest.fixture
def mock_user_repo():
    return MagicMock()

@pytest.fixture
def use_case(mock_user_repo):
    return LoginUseCase(user_repo=mock_user_repo)

@pytest.mark.asyncio
async def test_login_success(use_case, mock_user_repo):
    # Setup
    password = "secret_password"
    user = User(
        id=uuid.uuid4(),
        name="Test User",
        email="user@test.com",
        password_hash=hash_password(password),
        role=UserRole.CLIENT,
        is_active=True
    )
    
    mock_user_repo.get_by_email = AsyncMock(return_value=user)

    # Execute
    result = await use_case.execute(LoginInput(email="user@test.com", password=password))

    # Assert
    assert result.id == user.id
    assert result.email == user.email

@pytest.mark.asyncio
async def test_login_invalid_credentials(use_case, mock_user_repo):
    # Setup
    mock_user_repo.get_by_email = AsyncMock(return_value=None)

    # Execute & Assert
    with pytest.raises(UnauthorizedError):
        await use_case.execute(LoginInput(email="wrong@test.com", password="..."))

@pytest.mark.asyncio
async def test_login_wrong_password(use_case, mock_user_repo):
    # Setup
    user = User(
        id=uuid.uuid4(),
        name="Test User",
        email="user@test.com",
        password_hash=hash_password("correct_password"),
        role=UserRole.CLIENT,
        is_active=True
    )
    mock_user_repo.get_by_email = AsyncMock(return_value=user)

    # Execute & Assert
    with pytest.raises(UnauthorizedError):
        await use_case.execute(LoginInput(email="user@test.com", password="wrong_password"))
