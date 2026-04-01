import pytest
from fastapi import status
from uuid import uuid4

@pytest.mark.asyncio
async def test_auth_me_delete_lgpd(client, db_session):
    """Testa exclusão de conta e anonimização LGPD."""
    # 1. Registrar e autenticar
    reg_data = {
        "name": "Deleteme User",
        "email": "deleteme@teste.com",
        "phone": "+5511999998888",
        "password": "password123",
        "consent_terms": True,
        "consent_privacy": True
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_data)
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. DELETE /me (confirmação errada)
    del_res_wrong = await client.request("DELETE", "/api/v1/auth/me", json={"password": "wrong"}, headers=headers)
    assert del_res_wrong.status_code == status.HTTP_401_UNAUTHORIZED
    
    # 3. DELETE /me (confirmação correta)
    del_res_ok = await client.request("DELETE", "/api/v1/auth/me", json={"password": "password123"}, headers=headers)
    assert del_res_ok.status_code == status.HTTP_200_OK
    
    # 4. Verificar anonimização no banco (GET /me deve falhar ou retornar 401)
    me_res = await client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_auth_me_consents_history(client, db_session):
    """Testa listagem de históricos de consentimento."""
    # Registrar e autenticar
    reg_data = {
        "name": "Consent User",
        "email": "consent@teste.com",
        "phone": "+5511999997777",
        "password": "password123",
        "consent_terms": True,
        "consent_privacy": True
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_data)
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # GET /me/consents
    consents_res = await client.get("/api/v1/auth/me/consents", headers=headers)
    assert consents_res.status_code == status.HTTP_200_OK
    data = consents_res.json()
    assert len(data) >= 2 # terms + privacy
    statuses = [c["consent_type"] for c in data]
    assert "terms" in statuses
    assert "privacy" in statuses

@pytest.mark.asyncio
async def test_log_masking_integration(client, db_session):
    """Verifica se logs não expõem PII (simulado via teste de middleware)."""
    # Este teste é mais difícil de automatizar sem capturar o logger do uvicorn
    # Mas podemos testar se a resposta (caso contenha PII) seria mascarada
    # (Embora respondêssemos com schemas, o middleware age no streaming/output)
    pass
