import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from app.application.use_cases.create_review_use_case import CreateReviewUseCase, CreateReviewInput
from app.domain.entities.review import Review
from app.domain.entities.contract import Contract
from app.domain.entities.bid import Bid
from app.domain.exceptions import NotFoundError, UnauthorizedError

@pytest.mark.asyncio
async def test_create_review_success():
    # Setup
    review_repo = AsyncMock()
    contract_repo = AsyncMock()
    prof_repo = AsyncMock()
    
    contract_id = uuid.uuid4()
    client_user_id = uuid.uuid4()
    prof_id = uuid.uuid4()
    req_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    # Mock data
    contract = MagicMock(spec=Contract)
    contract.client_id = client_user_id
    contract.professional_id = prof_id
    contract.status = "completed"
    contract_repo.get_by_id.return_value = contract
    
    prof = MagicMock()
    prof.user_id = user_id
    prof_repo.get_by_id.return_value = prof
    
    review_repo.get_averages.return_value = {
        "total": 1,
        "avg_quality": 4.5,
        "avg_punctuality": 4.0,
        "avg_communication": 4.0,
        "avg_cleanliness": 4.0
    }
    contract_repo.count_completed_by_professional.return_value = 5
    
    review_repo.save.side_effect = lambda x: x
    
    use_case = CreateReviewUseCase(review_repo, contract_repo, prof_repo)
    
    input_data = CreateReviewInput(
        client_user_id=client_user_id,
        contract_id=contract_id,
        rating=5,
        text="Great service! This is a long enough review to be authentic."
    )
    
    # Execute
    result = await use_case.execute(input_data)
    
    # Assert
    assert result.rating == 5
    assert result.text == input_data.text
    assert result.is_authentic is True
    review_repo.save.assert_called_once()

@pytest.mark.asyncio
async def test_create_review_unauthorized():
    # Setup
    review_repo = AsyncMock()
    contract_repo = AsyncMock()
    prof_repo = AsyncMock()
    
    client_user_id = uuid.uuid4()
    other_client_id = uuid.uuid4()
    
    contract = MagicMock(spec=Contract)
    contract.client_id = other_client_id # Different client
    contract_repo.get_by_id.return_value = contract
    
    use_case = CreateReviewUseCase(review_repo, contract_repo, prof_repo)
    
    input_data = CreateReviewInput(
        client_user_id=client_user_id,
        contract_id=uuid.uuid4(),
        rating=5,
        text="..."
    )
    
    # Execute & Assert
    from app.domain.exceptions import BusinessRuleViolationError
    with pytest.raises(BusinessRuleViolationError):
        await use_case.execute(input_data)
