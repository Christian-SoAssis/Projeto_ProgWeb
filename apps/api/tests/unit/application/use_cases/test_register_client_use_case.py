import pytest
from unittest.mock import MagicMock, AsyncMock
import uuid
from app.application.use_cases.register_client_use_case import RegisterClientUseCase, RegisterClientInput
from app.domain.entities.user import User, UserRole
from app.domain.exceptions import BusinessRuleViolationError

@pytest.fixture
def mock_user_repo():
    return MagicMock()

@pytest.fixture
def mock_consent_repo():
    return MagicMock()

@pytest.fixture
def use_case(mock_user_repo, mock_consent_repo):
    return RegisterClientUseCase(
        user_repo=mock_user_repo,
        consent_repo=mock_consent_repo
    )

@pytest.mark.asyncio
async def test_register_client_success(use_case, mock_user_repo, mock_consent_repo):
    # Setup
    input_data = RegisterClientInput(
        name="Test Client",
        email="client@test.com",
        phone="123456789",
        password="password123",
        ip_address="127.0.0.1",
        user_agent="pytest"
    )
    
    # Mocks
    mock_user_repo.get_by_email = AsyncMock(return_value=None)
    mock_user_repo.save = AsyncMock()
    mock_consent_repo.save_all = AsyncMock()

    # Execute
    result = await use_case.execute(input_data)

    # Assert
    assert isinstance(result, User)
    assert result.email == input_data.email
    assert result.role == UserRole.CLIENT
    mock_user_repo.save.assert_called_once()
    mock_consent_repo.save_all.assert_called_once()

@pytest.mark.asyncio
async def test_register_client_email_taken(use_case, mock_user_repo):
    # Setup
    input_data = RegisterClientInput(
        name="Test Client",
        email="exists@test.com",
        phone="123456789",
        password="password123",
        ip_address="",
        user_agent=""
    )
    
    mock_user_repo.get_by_email = AsyncMock(return_value=MagicMock(spec=User))

    # Execute & Assert
    with pytest.raises(BusinessRuleViolationError) as exc:
        await use_case.execute(input_data)
    
    assert "Email já cadastrado" in str(exc.value)
