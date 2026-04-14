import pytest
from uuid import uuid4
from pydantic import ValidationError
from app.schemas.v1.bids import BidCreate, BidUpdate, BidResponse

def test_bid_create_valid():
    request_id = uuid4()
    data = {
        "request_id": request_id,
        "price_cents": 10000,
        "estimated_hours": 5,
        "message": "I can do it!"
    }
    bid = BidCreate(**data)
    assert bid.request_id == request_id
    assert bid.price_cents == 10000

def test_bid_create_invalid_price():
    with pytest.raises(ValidationError):
        BidCreate(request_id=uuid4(), price_cents=0)
    with pytest.raises(ValidationError):
        BidCreate(request_id=uuid4(), price_cents=-1)

def test_bid_create_invalid_hours():
    with pytest.raises(ValidationError):
        BidCreate(request_id=uuid4(), price_cents=1000, estimated_hours=0)

def test_bid_create_message_too_long():
    with pytest.raises(ValidationError):
        BidCreate(request_id=uuid4(), price_cents=1000, message="a" * 501)

def test_bid_update_valid():
    assert BidUpdate(status="accepted").status == "accepted"
    assert BidUpdate(status="rejected").status == "rejected"

def test_bid_update_invalid():
    with pytest.raises(ValidationError):
        BidUpdate(status="pending")
    with pytest.raises(ValidationError):
        BidUpdate(status="cancelled")

def test_bid_response_serialization():
    # Mock class to simulate ORM object
    class MockBid:
        def __init__(self):
            self.id = uuid4()
            self.request_id = uuid4()
            self.professional_id = uuid4()
            self.price_cents = 15000
            self.estimated_hours = 3
            self.message = "Test"
            self.status = "pending"
            from datetime import datetime, timezone
            self.created_at = datetime.now(timezone.utc)

    mock = MockBid()
    bid_resp = BidResponse.model_validate(mock)
    assert bid_resp.id == mock.id
    assert bid_resp.price_cents == 15000
