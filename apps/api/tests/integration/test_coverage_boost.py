import pytest
import asyncio
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from sqlalchemy import select
from fastapi import HTTPException

from app.models.user import User, UserRole
from app.models.professional import Professional
from app.models.request import Request
from app.models.category import Category
from app.models.contract import Contract
from app.models.review import Review
from app.models.bid import Bid
from app.services import matching_service, review_service, lgpd_service

@pytest.fixture
async def setup_data(db_session):
    # Basic category
    cat = Category(name="Teste", slug=f"teste-{uuid4().hex[:4]}", color="#FF0000")
    db_session.add(cat)
    
    # Client
    client = User(
        name="Client Test", 
        email=f"client-{uuid4().hex[:4]}@test.com", 
        password_hash="hash", 
        role=UserRole.CLIENT
    )
    db_session.add(client)
    
    # Professional
    prof_user = User(
        name="Prof Test", 
        email=f"prof-{uuid4().hex[:4]}@test.com", 
        password_hash="hash", 
        role=UserRole.PROFESSIONAL
    )
    db_session.add(prof_user)
    await db_session.flush()
    
    prof = Professional(
        user_id=prof_user.id,
        bio="Bio de teste com mais de dez caracteres",
        latitude=-23.55,
        longitude=-46.63,
        service_radius_km=10.0,
        is_verified=True
    )
    db_session.add(prof)
    await db_session.flush()
    await db_session.refresh(prof)
    await db_session.refresh(cat)
    
    # Associate prof with category
    from app.models.associations import professional_categories
    await db_session.execute(
        professional_categories.insert().values(professional_id=prof.id, category_id=cat.id)
    )
    
    await db_session.flush()
    return {"client": client, "professional": prof, "category": cat}

# --- Matching Service Tests ---

@pytest.mark.asyncio
async def test_matching_request_no_location(db_session, setup_data):
    req = Request(
        client_id=setup_data["client"].id,
        category_id=setup_data["category"].id,
        title="Request sem local",
        urgency="flexible",
        location=None # This might be tricky with PostGIS nullable=False, so let's check
    )
    # If location is NOT NULL in DB, we skip this or use a mock
    # matching_service checks if request.latitude is None
    from unittest.mock import MagicMock
    mock_request = MagicMock(spec=Request)
    mock_request.latitude = None
    mock_request.longitude = None
    mock_request.id = uuid4()
    
    matches = await matching_service.get_matches_v0(db_session, mock_request, setup_data["category"].id)
    assert matches == []

@pytest.mark.asyncio
async def test_matching_timeout(db_session, setup_data):
    req = Request(
        client_id=setup_data["client"].id,
        category_id=setup_data["category"].id,
        title="Request timeout",
        urgency="flexible",
        latitude=-23.55,
        longitude=-46.63
    )
    
    with patch("app.services.matching_service.get_matches_v0", side_effect=asyncio.TimeoutError):
        matches = await matching_service.get_matches(db_session, req)
        assert matches == []

@pytest.mark.asyncio
async def test_matching_generic_exception(db_session, setup_data):
    req = Request(
        client_id=setup_data["client"].id,
        category_id=setup_data["category"].id,
        title="Request error",
        urgency="flexible",
        latitude=-23.55,
        longitude=-46.63
    )
    
    with patch("app.services.matching_service.get_matches_v0", side_effect=Exception("Epic fail")):
        matches = await matching_service.get_matches(db_session, req)
        assert matches == []

# --- Review Service Tests ---

@pytest.mark.asyncio
async def test_create_review_contract_not_found(db_session):
    with pytest.raises(HTTPException) as exc:
        await review_service.create_review(db_session, uuid4(), uuid4(), 5, "Nice service")
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_create_review_not_owner(db_session, setup_data):
    req = Request(
        client_id=setup_data["client"].id,
        category_id=setup_data["category"].id,
        title="Request para contrato",
        urgency="flexible",
        latitude=-23.55,
        longitude=-46.63
    )
    db_session.add(req)
    await db_session.flush()
    
    # Create another client
    other_client = User(
        name="Other Client", 
        email=f"other-{uuid4().hex[:4]}@test.com", 
        password_hash="hash", 
        role=UserRole.CLIENT
    )
    db_session.add(other_client)
    await db_session.flush()

    contract = Contract(
        request_id=req.id,
        client_id=other_client.id, # Valid but not our setup client
        professional_id=setup_data["professional"].id,
        agreed_cents=1000,
        status="completed"
    )
    db_session.add(contract)
    await db_session.flush()
    
    with pytest.raises(HTTPException) as exc:
        await review_service.create_review(
            db_session, setup_data["client"].id, contract.id, 5, "Nice service"
        )
    assert exc.value.status_code == 403

@pytest.mark.asyncio
async def test_create_review_not_completed(db_session, setup_data):
    req = Request(
        client_id=setup_data["client"].id,
        category_id=setup_data["category"].id,
        title="Request para contrato 2",
        urgency="flexible",
        latitude=-23.55,
        longitude=-46.63
    )
    db_session.add(req)
    await db_session.flush()

    contract = Contract(
        request_id=req.id,
        client_id=setup_data["client"].id,
        professional_id=setup_data["professional"].id,
        agreed_cents=1000,
        status="active" # Not completed
    )
    db_session.add(contract)
    await db_session.flush()
    
    with pytest.raises(HTTPException) as exc:
        await review_service.create_review(
            db_session, setup_data["client"].id, contract.id, 5, "Nice service"
        )
    assert exc.value.status_code == 422

@pytest.mark.asyncio
async def test_review_authenticity_failure(db_session, setup_data):
    # Text too short
    assert review_service.is_review_authentic("Too short") is False
    # Text repetitive
    repetitive = "test test test test test test test test test test test test test"
    assert review_service.is_review_authentic(repetitive) is False

@pytest.mark.asyncio
async def test_create_review_success_and_recalculate(db_session, setup_data):
    req = Request(
        client_id=setup_data["client"].id,
        category_id=setup_data["category"].id,
        title="Request finalizado",
        urgency="flexible",
        latitude=-23.55,
        longitude=-46.63
    )
    db_session.add(req)
    await db_session.flush()

    contract = Contract(
        request_id=req.id,
        client_id=setup_data["client"].id,
        professional_id=setup_data["professional"].id,
        agreed_cents=2000,
        status="completed"
    )
    db_session.add(contract)
    await db_session.flush()

    # Create an authentic review
    review_text = "Ótimo serviço prestado pelo profissional, muito pontual e limpo."
    
    # Mock Gemini analysis to avoid API calls and ensure coverage of recalculate
    mock_scores = {
        "punctuality": 0.9,
        "quality": 1.0,
        "cleanliness": 0.8,
        "communication": 0.9
    }
    
    with patch("app.services.review_service._analyze_with_gemini", return_value=mock_scores):
        review = await review_service.create_review(
            db_session, setup_data["client"].id, contract.id, 5, review_text
        )
    
    assert review.id is not None
    assert review.is_authentic is True
    assert review.score_quality == 1.0
    
    # Check reputation update via fresh query
    res = await db_session.execute(
        select(Professional.reputation_score).where(Professional.id == setup_data["professional"].id)
    )
    new_score = res.scalar()
    assert new_score > 0

@pytest.mark.asyncio
async def test_list_professional_reviews(db_session, setup_data):
    reviews = await review_service.list_reviews_for_professional(
        db_session, setup_data["professional"].id
    )
    assert isinstance(reviews, list)

# --- LGPD Service Tests ---

def test_masking():
    assert lgpd_service.mask_cpf("123") == "123" # too short
    assert lgpd_service.mask_cnpj("123") == "123" # too short
    assert lgpd_service.mask_cpf("123.456.789-01") == "***.***.***-01"

@pytest.mark.asyncio
async def test_lgpd_check_can_delete_conflict(db_session, setup_data):
    req = Request(
        client_id=setup_data["client"].id,
        category_id=setup_data["category"].id,
        title="Request para contrato 3",
        urgency="flexible",
        latitude=-23.55,
        longitude=-46.63
    )
    db_session.add(req)
    await db_session.flush()

    contract = Contract(
        request_id=req.id,
        client_id=setup_data["client"].id,
        professional_id=setup_data["professional"].id,
        agreed_cents=1000,
        status="active"
    )
    db_session.add(contract)
    await db_session.flush()
    
    with pytest.raises(HTTPException) as exc:
        await lgpd_service.check_can_delete(db_session, setup_data["client"].id)
    assert exc.value.status_code == 409

@pytest.mark.asyncio
async def test_lgpd_cancel_pending_bids(db_session, setup_data):
    from app.models.bid import Bid
    req = Request(
        client_id=setup_data["client"].id,
        category_id=setup_data["category"].id,
        title="Request para lance",
        urgency="flexible",
        latitude=-23.55,
        longitude=-46.63
    )
    db_session.add(req)
    await db_session.flush()

    bid = Bid(
        request_id=req.id,
        professional_id=setup_data["professional"].id,
        price_cents=1000,
        status="pending"
    )
    db_session.add(bid)
    await db_session.flush()
    
    # First find user_id
    user_id = setup_data["professional"].user_id
    await lgpd_service.cancel_pending_bids(db_session, user_id)
    
    await db_session.refresh(bid)
    assert bid.status == "cancelled"

@pytest.mark.asyncio
async def test_lgpd_remove_docs_fail():
    # Mock shutil.rmtree to raise
    with patch("shutil.rmtree", side_effect=Exception("Disk error")):
        with patch("os.path.exists", return_value=True):
            await lgpd_service.remove_professional_documents(uuid4())
