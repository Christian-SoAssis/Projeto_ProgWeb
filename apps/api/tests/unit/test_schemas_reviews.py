import pytest
from uuid import uuid4
from pydantic import ValidationError
from app.schemas.v1.reviews import ReviewCreate, ReviewResponse

def test_rating_zero():
    with pytest.raises(ValidationError):
        ReviewCreate(contract_id=uuid4(), rating=0, text="Excellent service provided!")

def test_rating_six():
    with pytest.raises(ValidationError):
        ReviewCreate(contract_id=uuid4(), rating=6, text="Excellent service provided!")

def test_rating_negative():
    with pytest.raises(ValidationError):
        ReviewCreate(contract_id=uuid4(), rating=-1, text="Excellent service provided!")

def test_text_too_short():
    with pytest.raises(ValidationError):
        ReviewCreate(contract_id=uuid4(), rating=5, text="Short")

def test_text_empty():
    with pytest.raises(ValidationError):
        ReviewCreate(contract_id=uuid4(), rating=5, text="")

def test_text_too_long():
    with pytest.raises(ValidationError):
        ReviewCreate(contract_id=uuid4(), rating=5, text="x" * 2001)

def test_contract_id_invalid():
    with pytest.raises(ValidationError):
        ReviewCreate(contract_id="not-a-uuid", rating=5, text="Valid text here")

def test_rating_valid():
    for r in [1, 2, 3, 4, 5]:
        ReviewCreate(contract_id=uuid4(), rating=r, text="Valid text here")

def test_text_minimum():
    ReviewCreate(contract_id=uuid4(), rating=5, text="a" * 10)

def test_text_maximum():
    ReviewCreate(contract_id=uuid4(), rating=5, text="a" * 2000)

def test_review_response_serialization():
    # Mock class to simulate ORM object
    class MockReview:
        def __init__(self):
            self.id = uuid4()
            self.contract_id = uuid4()
            self.reviewer_id = uuid4()
            self.reviewee_id = uuid4()
            self.rating = 5
            self.text = "Excellent"
            self.score_punctuality = 0.9
            self.score_quality = 1.0
            self.score_cleanliness = 0.8
            self.score_communication = 1.0
            self.is_authentic = True
            from datetime import datetime, timezone
            self.created_at = datetime.now(timezone.utc)

    mock = MockReview()
    review_resp = ReviewResponse.model_validate(mock)
    assert review_resp.id == mock.id
    assert review_resp.rating == 5
    assert review_resp.is_authentic is True
    assert review_resp.score_punctuality == 0.9
