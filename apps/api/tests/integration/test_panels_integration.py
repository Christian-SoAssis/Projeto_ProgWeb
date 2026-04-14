import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import datetime, timezone
from geoalchemy2 import WKTElement
from sqlalchemy import text

from app.models.user import User, UserRole
from app.models.professional import Professional
from app.models.category import Category
from app.models.request import Request
from app.models.contract import Contract
from app.models.favorite import Favorite
from app.models.notification import Notification
from app.core.security import create_access_token

@pytest_asyncio.fixture
async def panels_setup(db_session, async_client):
    """Cria client, professional verificado com contrato e review."""
    client_user = User(
        email=f"client_{uuid4().hex[:6]}@test.com",
        name="Cliente Teste", password_hash="hash",
        role=UserRole.CLIENT, is_active=True
    )
    db_session.add(client_user)

    prof_user = User(
        email=f"prof_{uuid4().hex[:6]}@test.com",
        name="Profissional Teste", password_hash="hash",
        role=UserRole.PROFESSIONAL, is_active=True
    )
    db_session.add(prof_user)
    await db_session.flush()

    prof = Professional(
        user_id=prof_user.id,
        bio="Profissional experiente em hidráulica",
        latitude=-21.55, longitude=-45.42,
        service_radius_km=20.0,
        hourly_rate_cents=8000,
        reputation_score=4.0,
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

    # Associar categoria ao profissional
    await db_session.execute(
        text("INSERT INTO professional_categories (professional_id, category_id) VALUES (:pid, :cid)"),
        {"pid": prof.id, "cid": cat.id}
    )

    req = Request(
        client_id=client_user.id,
        category_id=cat.id,
        title="Torneira vazando urgente",
        urgency="immediate",
        location=WKTElement("POINT(-45.42 -21.55)", srid=4326),
        status="matched"
    )
    db_session.add(req)
    await db_session.flush()

    contract = Contract(
        request_id=req.id,
        professional_id=prof.id,
        client_id=client_user.id,
        agreed_cents=20000,
        status="completed",
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
    )
    db_session.add(contract)
    await db_session.flush()

    client_token = create_access_token(data={"sub": str(client_user.id)})
    prof_token = create_access_token(data={"sub": str(prof_user.id)})

    return {
        "client": client_user,
        "prof_user": prof_user,
        "professional": prof,
        "contract": contract,
        "category": cat,
        "client_headers": {"Authorization": f"Bearer {client_token}"},
        "prof_headers": {"Authorization": f"Bearer {prof_token}"},
    }

# --- Search ---
@pytest.mark.asyncio
async def test_search_professionals_by_location(async_client, panels_setup):
    """Busca geo retorna profissionais na área."""
    resp = await async_client.get("/api/v1/search/professionals", params={
        "lat": -21.55, "lng": -45.42, "radius_km": 30
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert any(p["id"] == str(panels_setup["professional"].id) for p in data)

@pytest.mark.asyncio
async def test_search_professionals_by_text(async_client, panels_setup):
    """Busca por texto retorna profissional com bio correspondente."""
    resp = await async_client.get("/api/v1/search/professionals", params={
        "q": "hidráulica", "lat": -21.55, "lng": -45.42, "radius_km": 50
    })
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_search_professionals_empty_area(async_client, panels_setup):
    """Área sem profissionais retorna lista vazia."""
    resp = await async_client.get("/api/v1/search/professionals", params={
        "lat": 0.0, "lng": 0.0, "radius_km": 1
    })
    assert resp.status_code == 200
    assert resp.json() == []

# --- Perfil do Profissional ---
@pytest.mark.asyncio
async def test_get_professional_me(async_client, panels_setup):
    resp = await async_client.get(
        "/api/v1/professionals/me",
        headers=panels_setup["prof_headers"]
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == str(panels_setup["professional"].user_id)

@pytest.mark.asyncio
async def test_get_professional_me_not_professional(async_client, panels_setup):
    """Cliente tentando acessar /professionals/me → 403."""
    resp = await async_client.get(
        "/api/v1/professionals/me",
        headers=panels_setup["client_headers"]
    )
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_patch_professional_me(async_client, panels_setup):
    resp = await async_client.patch(
        "/api/v1/professionals/me",
        json={"bio": "Bio atualizada com mais de dez caracteres."},
        headers=panels_setup["prof_headers"]
    )
    assert resp.status_code == 200
    assert "atualizada" in resp.json()["bio"]

# --- Métricas ---
@pytest.mark.asyncio
async def test_get_professional_metrics(async_client, panels_setup):
    resp = await async_client.get(
        "/api/v1/professionals/me/metrics",
        headers=panels_setup["prof_headers"]
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total_earnings_cents" in data
    assert "completed_jobs" in data
    assert "reputation_score" in data
    assert data["completed_jobs"] == 1
    assert data["total_earnings_cents"] == 20000

# --- Favoritos ---
@pytest.mark.asyncio
async def test_add_favorite(async_client, panels_setup):
    resp = await async_client.post(
        "/api/v1/favorites",
        json={"professional_id": str(panels_setup["professional"].id)},
        headers=panels_setup["client_headers"]
    )
    assert resp.status_code == 201

@pytest.mark.asyncio
async def test_add_favorite_duplicate(async_client, panels_setup, db_session):
    """Favorito duplicado → 409."""
    fav = Favorite(
        client_id=panels_setup["client"].id,
        professional_id=panels_setup["professional"].id
    )
    db_session.add(fav)
    await db_session.flush()

    resp = await async_client.post(
        "/api/v1/favorites",
        json={"professional_id": str(panels_setup["professional"].id)},
        headers=panels_setup["client_headers"]
    )
    assert resp.status_code == 409

@pytest.mark.asyncio
async def test_list_favorites(async_client, panels_setup, db_session):
    fav = Favorite(
        client_id=panels_setup["client"].id,
        professional_id=panels_setup["professional"].id
    )
    db_session.add(fav)
    await db_session.flush()

    resp = await async_client.get(
        "/api/v1/favorites",
        headers=panels_setup["client_headers"]
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1

@pytest.mark.asyncio
async def test_remove_favorite(async_client, panels_setup, db_session):
    fav = Favorite(
        client_id=panels_setup["client"].id,
        professional_id=panels_setup["professional"].id
    )
    db_session.add(fav)
    await db_session.flush()

    resp = await async_client.delete(
        f"/api/v1/favorites/{panels_setup['professional'].id}",
        headers=panels_setup["client_headers"]
    )
    assert resp.status_code == 204

# --- Notificações ---
@pytest.mark.asyncio
async def test_list_notifications_empty(async_client, panels_setup):
    resp = await async_client.get(
        "/api/v1/notifications",
        headers=panels_setup["client_headers"]
    )
    assert resp.status_code == 200
    assert resp.json() == []

@pytest.mark.asyncio
async def test_mark_notifications_read(async_client, panels_setup, db_session):
    notif = Notification(
        user_id=panels_setup["client"].id,
        type="bid_received",
        payload={"bid_id": str(uuid4())},
    )
    db_session.add(notif)
    await db_session.flush()

    resp = await async_client.patch(
        "/api/v1/notifications/mark-read",
        json={"notification_ids": [str(notif.id)]},
        headers=panels_setup["client_headers"]
    )
    assert resp.status_code == 200
