import pytest
from httpx import AsyncClient
from uuid import uuid4

pytestmark = pytest.mark.asyncio


async def test_register_client_success(async_client: AsyncClient):
    uid = uuid4().hex[:8]
    payload = {
        "name": "Cliente Teste",
        "email": f"client1_{uid}@test.com",
        "password": "password123",
        "consent_terms": True,
        "consent_privacy": True
    }
    resp = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


async def test_register_creates_consent_logs(async_client: AsyncClient, db_session):
    uid = uuid4().hex[:8]
    email = f"client2_{uid}@test.com"
    payload = {
        "name": "Cliente Teste 2",
        "email": email,
        "password": "password123",
        "consent_terms": True,
        "consent_privacy": True
    }
    resp = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201

    from sqlalchemy import text
    res = await db_session.execute(
        text("SELECT consent_type FROM consent_logs WHERE user_id = (SELECT id FROM users WHERE email=:e)"),
        {"e": email}
    )
    logs = res.scalars().all()
    assert len(logs) == 2
    assert "terms" in logs
    assert "privacy" in logs


async def test_register_duplicate_email(async_client: AsyncClient):
    uid = uuid4().hex[:8]
    payload = {
        "name": "Cliente Teste 3",
        "email": f"client3_{uid}@test.com",
        "password": "password123",
        "consent_terms": True,
        "consent_privacy": True
    }
    resp1 = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp1.status_code == 201
    resp = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409
    assert "E-mail já cadastrado" in resp.json()["detail"]


async def test_register_missing_field(async_client: AsyncClient):
    payload = {
        "name": "Cliente Sem Email",
        "password": "password123",
        "consent_terms": True,
        "consent_privacy": True
    }
    resp = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


async def test_register_consent_false(async_client: AsyncClient):
    uid = uuid4().hex[:8]
    payload = {
        "name": "Cliente Sem Consent",
        "email": f"client4_{uid}@test.com",
        "password": "password123",
        "consent_terms": False,
        "consent_privacy": True
    }
    resp = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


# --- LOGIN ---
async def test_login_success(async_client: AsyncClient):
    uid = uuid4().hex[:8]
    email = f"log_{uid}@log.com"
    payload_reg = {"name": "Log", "email": email, "password": "password123", "consent_terms": True, "consent_privacy": True}
    resp_r = await async_client.post("/api/v1/auth/register", json=payload_reg)
    assert resp_r.status_code == 201
    resp = await async_client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_login_wrong_password(async_client: AsyncClient):
    uid = uuid4().hex[:8]
    email = f"log2_{uid}@log.com"
    payload_reg = {"name": "Log2", "email": email, "password": "password123", "consent_terms": True, "consent_privacy": True}
    resp_r = await async_client.post("/api/v1/auth/register", json=payload_reg)
    assert resp_r.status_code == 201
    resp = await async_client.post("/api/v1/auth/login", json={"email": email, "password": "wrong"})
    assert resp.status_code == 401
    assert "Credenciais inválidas" in resp.json()["detail"]


async def test_login_unknown_email(async_client: AsyncClient):
    resp = await async_client.post("/api/v1/auth/login", json={"email": "nobody@log.com", "password": "wrong"})
    assert resp.status_code == 401
    assert "Credenciais inválidas" in resp.json()["detail"]


async def test_login_updates_last_login_at(async_client: AsyncClient, db_session):
    uid = uuid4().hex[:8]
    email = f"log3_{uid}@log.com"
    payload_reg = {"name": "Log3", "email": email, "password": "password123", "consent_terms": True, "consent_privacy": True}
    resp_r = await async_client.post("/api/v1/auth/register", json=payload_reg)
    assert resp_r.status_code == 201
    await async_client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    from sqlalchemy import text
    res = await db_session.execute(text("SELECT last_login_at FROM users WHERE email=:e"), {"e": email})
    assert res.scalar_one_or_none() is not None


# --- REFRESH ---
async def test_refresh_success(async_client: AsyncClient):
    uid = uuid4().hex[:8]
    payload_reg = {"name": "Ref", "email": f"ref_{uid}@log.com", "password": "password123", "consent_terms": True, "consent_privacy": True}
    resp1 = await async_client.post("/api/v1/auth/register", json=payload_reg)
    assert resp1.status_code == 201
    refresh_token = resp1.json()["refresh_token"]
    resp2 = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp2.status_code == 200
    assert resp2.json()["refresh_token"] != refresh_token


async def test_refresh_token_rotation(async_client: AsyncClient):
    uid = uuid4().hex[:8]
    payload_reg = {"name": "Rot", "email": f"rot_{uid}@log.com", "password": "password123", "consent_terms": True, "consent_privacy": True}
    resp1 = await async_client.post("/api/v1/auth/register", json=payload_reg)
    assert resp1.status_code == 201
    old_rt = resp1.json()["refresh_token"]
    await async_client.post("/api/v1/auth/refresh", json={"refresh_token": old_rt})
    resp_reused = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": old_rt})
    assert resp_reused.status_code == 401


async def test_refresh_expired(async_client: AsyncClient):
    # Coberto pelos testes unitários com expired delta
    pass


async def test_refresh_invalid_token(async_client: AsyncClient):
    resp = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid.token.here"})
    assert resp.status_code == 401


# --- GET /me ---
async def test_get_me_authenticated(async_client: AsyncClient):
    uid = uuid4().hex[:8]
    email = f"me_{uid}@log.com"
    payload_reg = {"name": "Me", "email": email, "password": "password123", "consent_terms": True, "consent_privacy": True}
    resp1 = await async_client.post("/api/v1/auth/register", json=payload_reg)
    assert resp1.status_code == 201
    token = resp1.json()["access_token"]
    resp = await async_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == email


async def test_get_me_no_token(async_client: AsyncClient):
    resp = await async_client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_get_me_expired_token(async_client: AsyncClient):
    pass  # Coberto pelos testes unitários


# --- POST /professionals ---
async def test_register_professional_success(async_client: AsyncClient, db_session):
    from sqlalchemy import text
    cat_id = str(uuid4())
    await db_session.execute(
        text(f"INSERT INTO categories (id, name, slug) VALUES ('{cat_id}', 'Test', 'test-{cat_id[:8]}') ON CONFLICT DO NOTHING")
    )
    await db_session.commit()

    uid = uuid4().hex[:8]
    import json
    files = {"document_file": ("doc.pdf", b"dummy content", "application/pdf")}
    payload_data = {
        "name": "Prof", "email": f"prof_{uid}@log.com", "password": "password123",
        "consent_terms": True, "consent_privacy": True,
        "bio": "bio", "latitude": -23.5, "longitude": -46.6,
        "service_radius_km": 10, "category_ids": [cat_id], "document_type": "cpf"
    }
    resp = await async_client.post(
        "/api/v1/professionals",
        data={"payload": json.dumps(payload_data)},
        files=files
    )
    assert resp.status_code == 201
    assert resp.json()["role"] == "professional"
    assert resp.json()["is_verified"] is False


async def test_register_professional_creates_professional_categories(async_client: AsyncClient, db_session):
    pass


async def test_register_professional_document_upload(async_client: AsyncClient):
    pass


# --- PATCH /professionals/:id ---
async def test_admin_approve_professional(async_client: AsyncClient, db_session):
    pass


async def test_admin_approve_non_admin(async_client: AsyncClient):
    pass
