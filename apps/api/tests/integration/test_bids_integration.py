import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import datetime, timezone
from geoalchemy2 import WKTElement

from app.models.user import User, UserRole
from app.models.professional import Professional
from app.models.category import Category
from app.models.request import Request
from app.models.bid import Bid
from app.core.security import create_access_token

@pytest_asyncio.fixture
async def bid_setup(db_session):
    """Cria client, professional verificado, categoria, request e tokens."""
    # 1. Criar cliente
    client_user = User(
        email=f"client_{uuid4().hex[:6]}@test.com",
        name="Cliente", password_hash="hash",
        role=UserRole.CLIENT, is_active=True
    )
    db_session.add(client_user)

    # 2. Criar profissional verificado
    prof_user = User(
        email=f"prof_{uuid4().hex[:6]}@test.com",
        name="Profissional", password_hash="hash",
        role=UserRole.PROFESSIONAL, is_active=True
    )
    db_session.add(prof_user)
    await db_session.flush()

    prof = Professional(
        user_id=prof_user.id,
        bio="Profissional experiente",
        latitude=-21.55, longitude=-45.42,
        service_radius_km=20.0,
        hourly_rate_cents=8000,
        reputation_score=4.5,
        is_verified=True
    )
    db_session.add(prof)

    # 3. Criar categoria e request
    cat = Category(
        name="Hidráulica",
        slug=f"hid_{uuid4().hex[:4]}",
        color="#1a9878"
    )
    db_session.add(cat)
    await db_session.flush()

    req = Request(
        client_id=client_user.id,
        category_id=cat.id,
        title="Torneira vazando",
        urgency="immediate",
        location=WKTElement("POINT(-45.42 -21.55)", srid=4326),
        status="open"
    )
    db_session.add(req)
    await db_session.flush()

    # Tokens
    client_token = create_access_token(data={"sub": str(client_user.id)})
    prof_token = create_access_token(data={"sub": str(prof_user.id)})

    return {
        "client": client_user,
        "prof_user": prof_user,
        "professional": prof,
        "request": req,
        "category": cat,
        "client_headers": {"Authorization": f"Bearer {client_token}"},
        "prof_headers": {"Authorization": f"Bearer {prof_token}"},
    }

@pytest.mark.asyncio
async def test_create_bid_success(async_client, bid_setup):
    resp = await async_client.post("/api/v1/bids", json={
        "request_id": str(bid_setup["request"].id),
        "price_cents": 15000,
        "message": "Posso resolver hoje",
        "estimated_hours": 2
    }, headers=bid_setup["prof_headers"])
    assert resp.status_code == 201
    data = resp.json()
    assert data["price_cents"] == 15000
    assert data["status"] == "pending"

@pytest.mark.asyncio
async def test_create_bid_unverified_professional(async_client, db_session, bid_setup):
    # Criar prof não verificado
    unv_user = User(email=f"unv_{uuid4().hex[:6]}@test.com", name="Unv",
                    password_hash="hash", role=UserRole.PROFESSIONAL, is_active=True)
    db_session.add(unv_user)
    await db_session.flush()
    unv_prof = Professional(user_id=unv_user.id, bio="bio aqui para teste",
                            latitude=-21.55, longitude=-45.42,
                            service_radius_km=20.0, hourly_rate_cents=5000,
                            reputation_score=0.0, is_verified=False)
    db_session.add(unv_prof)
    await db_session.flush()
    token = create_access_token(data={"sub": str(unv_user.id)})
    resp = await async_client.post("/api/v1/bids", json={
        "request_id": str(bid_setup["request"].id),
        "price_cents": 10000
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_list_bids_for_request(async_client, bid_setup, db_session):
    bid = Bid(
        request_id=bid_setup["request"].id,
        professional_id=bid_setup["professional"].id,
        price_cents=20000, status="pending"
    )
    db_session.add(bid)
    await db_session.flush()
    resp = await async_client.get(
        f"/api/v1/requests/{bid_setup['request'].id}/bids",
        headers=bid_setup["client_headers"]
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1

@pytest.mark.asyncio
async def test_accept_bid_creates_contract(async_client, bid_setup, db_session):
    bid = Bid(
        request_id=bid_setup["request"].id,
        professional_id=bid_setup["professional"].id,
        price_cents=25000, status="pending"
    )
    db_session.add(bid)
    await db_session.flush()
    resp = await async_client.patch(
        f"/api/v1/bids/{bid.id}",
        json={"status": "accepted"},
        headers=bid_setup["client_headers"]
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["bid"]["status"] == "accepted"
    assert data["contract"]["agreed_cents"] == 25000
