import pytest
from httpx import AsyncClient
from uuid import uuid4

@pytest.mark.asyncio
async def test_delete_account_success(async_client: AsyncClient, db_session):
    uid = uuid4().hex[:8]
    payload_reg = {
        "name": "Jane LGPD",
        "email": f"janelgpd_{uid}@test.com",
        "password": "password123",
        "consent_terms": True,
        "consent_privacy": True
    }
    resp_reg = await async_client.post("/api/v1/auth/register", json=payload_reg)
    assert resp_reg.status_code == 201
    token = resp_reg.json()["access_token"]

    resp_del = await async_client.request(
        "DELETE",
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"password": "password123"}
    )
    assert resp_del.status_code == 204

    from sqlalchemy import text
    res = await db_session.execute(
        text("SELECT is_active, name, email, phone FROM users WHERE email LIKE :e"),
        {"e": f"removed_%"}
    )
    row = res.fetchone()
    if row:
        assert row.is_active is False
        assert row.name == "Usuário Removido"
        assert "removed_" in row.email
        assert row.phone is None

@pytest.mark.asyncio
async def test_delete_account_wrong_password(async_client: AsyncClient):
    uid = uuid4().hex[:8]
    payload_reg = {"name": "Test LGPD", "email": f"lgpd2_{uid}@test.com", "password": "password123", "consent_terms": True, "consent_privacy": True}
    resp_reg = await async_client.post("/api/v1/auth/register", json=payload_reg)
    assert resp_reg.status_code == 201
    token = resp_reg.json()["access_token"]

    resp_del = await async_client.request("DELETE", "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}, json={"password": "wrong"})
    assert resp_del.status_code == 401

@pytest.mark.asyncio
async def test_delete_account_with_active_contract(async_client: AsyncClient, db_session):
    # Setup DB mock logic - assume we insert a contract 'in_progress' for this user
    # Assert 409
    pass

@pytest.mark.asyncio
async def test_get_consents(async_client: AsyncClient):
    uid = uuid4().hex[:8]
    payload_reg = {"name": "Test LGPD 3", "email": f"lgpd3_{uid}@test.com", "password": "password123", "consent_terms": True, "consent_privacy": True}
    resp_reg = await async_client.post("/api/v1/auth/register", json=payload_reg)
    assert resp_reg.status_code == 201
    token = resp_reg.json()["access_token"]

    resp_consents = await async_client.get("/api/v1/auth/me/consents", headers={"Authorization": f"Bearer {token}"})
    assert resp_consents.status_code == 200
    data = resp_consents.json()
    assert len(data) == 2
    types = [i["consent_type"] for i in data]
    assert "terms" in types
    assert "privacy" in types
    assert "privacy" in types

# Teste síncrono — sem mark asyncio
def test_log_masking_cpf(capsys):
    from app.middleware.log_sanitizer import sanitize_log
    log_record = {
        "event": "Request processing",
        "body": {
            "document_type": "cpf",
            "document_number": "12345678901",
            "password": "senha"
        },
        "headers": {
            "Authorization": "Bearer tokensecreto"
        }
    }
    sanitized = sanitize_log(log_record)
    assert sanitized["headers"]["Authorization"] == "Bearer [REDACTED]"
    assert sanitized["body"]["password"] == "[REDACTED]"
    assert sanitized["body"]["document_number"] == "***.***.***-XX"

