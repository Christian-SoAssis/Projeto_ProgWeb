import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import datetime, timezone
from geoalchemy2 import WKTElement

from app.models.user import User, UserRole
from app.models.professional import Professional
from app.models.category import Category
from app.models.request import Request
from app.models.contract import Contract
from app.models.review import Review
from app.core.security import create_access_token

@pytest_asyncio.fixture
async def review_setup(db_session):
    """Cria usuários, profissional, request, bid e contrato completo."""
    # Cliente
    client_user = User(
        email=f"client_{uuid4().hex[:6]}@test.com",
        name="Cliente", password_hash="hash",
        role=UserRole.CLIENT, is_active=True
    )
    db_session.add(client_user)

    # Profissional
    prof_user = User(
        email=f"prof_{uuid4().hex[:6]}@test.com",
        name="Profissional", password_hash="hash",
        role=UserRole.PROFESSIONAL, is_active=True
    )
    db_session.add(prof_user)
    await db_session.flush()

    prof = Professional(
        user_id=prof_user.id,
        bio="Bio do profissional experiente",
        latitude=-21.55, longitude=-45.42,
        service_radius_km=20.0,
        hourly_rate_cents=8000,
        reputation_score=0.0,
        is_verified=True
    )
    db_session.add(prof)

    cat = Category(
        name="Hidráulica",
        slug=f"hid_{uuid4().hex[:4]}",
        color="#0000FF"
    )
    db_session.add(cat)
    await db_session.flush()

    req = Request(
        client_id=client_user.id,
        category_id=cat.id,
        title="Torneira vazando",
        urgency="immediate",
        location=WKTElement("POINT(-45.42 -21.55)", srid=4326),
        status="matched"
    )
    db_session.add(req)
    await db_session.flush()

    # Contrato com status 'completed'
    contract = Contract(
        request_id=req.id,
        professional_id=prof.id,
        client_id=client_user.id,
        agreed_cents=15000,
        status="completed",
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
    )
    db_session.add(contract)
    await db_session.flush()

    client_token = create_access_token(data={"sub": str(client_user.id)})

    return {
        "client": client_user,
        "prof_user": prof_user,
        "professional": prof,
        "request": req,
        "contract": contract,
        "client_headers": {"Authorization": f"Bearer {client_token}"},
    }

@pytest.mark.asyncio
async def test_create_review_success(async_client, review_setup):
    """Cliente cria review após contrato completed."""
    resp = await async_client.post("/api/v1/reviews", json={
        "contract_id": str(review_setup["contract"].id),
        "rating": 5,
        "text": "Profissional excelente, muito pontual e organizado."
    }, headers=review_setup["client_headers"])
    assert resp.status_code == 201
    data = resp.json()
    assert data["rating"] == 5
    assert data["is_authentic"] is True

@pytest.mark.asyncio
async def test_create_review_contract_not_completed(async_client, review_setup, db_session):
    """Contrato não concluído → 422."""
    review_setup["contract"].status = "active"
    await db_session.flush()
    resp = await async_client.post("/api/v1/reviews", json={
        "contract_id": str(review_setup["contract"].id),
        "rating": 4,
        "text": "Profissional muito bom e atencioso."
    }, headers=review_setup["client_headers"])
    assert resp.status_code == 422

@pytest.mark.asyncio
async def test_create_review_duplicate(async_client, review_setup, db_session):
    """Review duplicada → 409."""
    review = Review(
        contract_id=review_setup["contract"].id,
        reviewer_id=review_setup["client"].id,
        reviewee_id=review_setup["prof_user"].id,
        rating=4,
        text="Primeira review deste contrato.",
        is_authentic=True,
    )
    db_session.add(review)
    await db_session.flush()

    resp = await async_client.post("/api/v1/reviews", json={
        "contract_id": str(review_setup["contract"].id),
        "rating": 3,
        "text": "Tentativa de segunda review aqui."
    }, headers=review_setup["client_headers"])
    assert resp.status_code == 409

@pytest.mark.asyncio
async def test_list_reviews_for_professional(async_client, review_setup, db_session):
    """GET /professionals/:id/reviews retorna reviews do profissional."""
    review = Review(
        contract_id=review_setup["contract"].id,
        reviewer_id=review_setup["client"].id,
        reviewee_id=review_setup["prof_user"].id,
        rating=5,
        text="Excelente trabalho realizado com qualidade.",
        is_authentic=True,
    )
    db_session.add(review)
    await db_session.flush()

    resp = await async_client.get(
        f"/api/v1/professionals/{review_setup['professional'].id}/reviews"
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1

@pytest.mark.asyncio
async def test_reputation_score_updated_after_review(async_client, review_setup, db_session):
    """Após review autêntica, reputation_score do profissional é atualizado."""
    initial_score = review_setup["professional"].reputation_score

    resp = await async_client.post("/api/v1/reviews", json={
        "contract_id": str(review_setup["contract"].id),
        "rating": 5,
        "text": "Profissional muito competente, trabalho excelente."
    }, headers=review_setup["client_headers"])
    assert resp.status_code == 201

    await db_session.refresh(review_setup["professional"])
    # reputation_score deve ter mudado
    assert review_setup["professional"].reputation_score != initial_score
