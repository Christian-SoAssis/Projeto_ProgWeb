import pytest
import uuid
from unittest.mock import AsyncMock
from app.application.use_cases.list_professional_reviews_use_case import ListProfessionalReviewsUseCase
from app.domain.entities.review import Review
from app.domain.exceptions import EntityNotFoundError

@pytest.mark.asyncio
async def test_list_reviews_success():
    # Setup
    review_repo = AsyncMock()
    
    prof_id = uuid.uuid4()
    
    review_repo.list_by_professional.return_value = [
        Review(id=uuid.uuid4(), contract_id=uuid.uuid4(), reviewer_id=uuid.uuid4(), reviewee_id=prof_id, rating=5, text="A")
    ]
    
    use_case = ListProfessionalReviewsUseCase(review_repo)
    
    # Execute
    result = await use_case.execute(prof_id)
    
    # Assert
    assert len(result) == 1
    review_repo.list_by_professional.assert_called_once_with(prof_id)
