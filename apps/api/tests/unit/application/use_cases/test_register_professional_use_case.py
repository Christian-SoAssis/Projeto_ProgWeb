import pytest
from unittest.mock import MagicMock, AsyncMock
import uuid
from app.application.use_cases.register_professional_use_case import RegisterProfessionalUseCase, RegisterProfessionalInput
from app.domain.entities.user import User, UserRole
from app.domain.entities.professional import Professional
from app.domain.exceptions import BusinessRuleViolationError

@pytest.fixture
def mock_user_repo():
    return MagicMock()

@pytest.fixture
def mock_prof_repo():
    return MagicMock()

@pytest.fixture
def mock_consent_repo():
    return MagicMock()

@pytest.fixture
def mock_file_storage():
    return MagicMock()

@pytest.fixture
def use_case(mock_user_repo, mock_prof_repo, mock_consent_repo, mock_file_storage):
    return RegisterProfessionalUseCase(
        user_repo=mock_user_repo,
        prof_repo=mock_prof_repo,
        consent_repo=mock_consent_repo,
        file_storage=mock_file_storage
    )

@pytest.mark.asyncio
async def test_register_professional_success(use_case, mock_user_repo, mock_prof_repo, mock_consent_repo, mock_file_storage):
    # Setup
    input_data = RegisterProfessionalInput(
        name="Test Prof",
        email="prof@test.com",
        phone="123456789",
        password="password123",
        bio="I am a professional",
        latitude=10.0,
        longitude=20.0,
        service_radius_km=50.0,
        hourly_rate_cents=5000,
        document_type="ID",
        document=MagicMock(), # Mock file object
        category_ids=[uuid.uuid4()],
        ip_address="127.0.0.1",
        user_agent="pytest"
    )
    
    # Mocks
    mock_user_repo.get_by_email = AsyncMock(return_value=None)
    mock_user_repo.save = AsyncMock()
    mock_prof_repo.save = AsyncMock(side_effect=lambda p: p) # Return the input object
    mock_consent_repo.save_all = AsyncMock()
    mock_file_storage.save_image = AsyncMock(return_value="path/to/doc")

    # Execute
    result = await use_case.execute(input_data)

    # Assert
    assert isinstance(result, Professional)
    assert result.email == input_data.email
    mock_user_repo.save.assert_called_once()
    mock_prof_repo.save.assert_called_once()
    mock_consent_repo.save_all.assert_called_once()
    mock_file_storage.save_image.assert_called_once()

@pytest.mark.asyncio
async def test_register_professional_email_taken(use_case, mock_user_repo):
    # Setup
    input_data = RegisterProfessionalInput(
        name="Test Prof",
        email="exists@test.com",
        phone="123456789",
        password="password123",
        bio="...", latitude=0, longitude=0, service_radius_km=0,
        hourly_rate_cents=100,
        document_type="ID", document=None, category_ids=[],
        ip_address="", user_agent=""
    )
    
    mock_user_repo.get_by_email = AsyncMock(return_value=MagicMock(spec=User))

    # Execute & Assert
    with pytest.raises(BusinessRuleViolationError) as exc:
        await use_case.execute(input_data)
    
    assert "Email já cadastrado" in str(exc.value)
