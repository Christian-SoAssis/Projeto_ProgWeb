import pytest
import uuid
from pydantic import ValidationError
from app.schemas.v1.matching import MatchResponse

def test_match_response_valid():
    data = {
        "id": uuid.uuid4(),
        "user_id": uuid.uuid4(),
        "bio": "Profissional experiente",
        "latitude": -21.55,
        "longitude": -45.42,
        "service_radius_km": 20.0,
        "hourly_rate_cents": 5000,
        "reputation_score": 4.5,
        "is_verified": True,
        "distance_km": 3.2,
    }
    m = MatchResponse(**data)
    assert m.distance_km == 3.2
    assert m.is_verified is True

def test_match_response_distance_required():
    # distance_km ausente → ValidationError
    data = {
        "id": uuid.uuid4(),
        "user_id": uuid.uuid4(),
        "bio": "Profissional experiente",
        "latitude": -21.55,
        "longitude": -45.42,
        "service_radius_km": 20.0,
        "hourly_rate_cents": 5000,
        "reputation_score": 4.5,
        "is_verified": True,
    }
    with pytest.raises(ValidationError):
        MatchResponse(**data)

def test_match_response_negative_distance():
    # distance_km negativo → ValidationError (ge=0)
    data = {
        "id": uuid.uuid4(),
        "user_id": uuid.uuid4(),
        "bio": "Profissional experiente",
        "latitude": -21.55,
        "longitude": -45.42,
        "service_radius_km": 20.0,
        "hourly_rate_cents": 5000,
        "reputation_score": 4.5,
        "is_verified": True,
        "distance_km": -1.0,
    }
    with pytest.raises(ValidationError):
        MatchResponse(**data)
