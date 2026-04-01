import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from uuid import uuid4

# Importações planejadas
try:
    from app.core import security
    from app.services import lgpd_service
except ImportError:
    pass

def test_password_hashing():
    """Testa hash_password e verify_password."""
    password = "secret_password"
    hashed = security.hash_password(password)
    assert hashed != password
    assert security.verify_password(password, hashed) is True
    assert security.verify_password("wrong_password", hashed) is False

def test_jwt_token_generation_and_decoding():
    """Testa criação e decodificação de tokens JWT."""
    user_id = str(uuid4())
    data = {"sub": user_id, "role": "client"}
    
    # Access Token (baseado no config, exp kira 15 min)
    access_token = security.create_access_token(data)
    decoded = security.decode_token(access_token)
    assert decoded["sub"] == user_id
    assert decoded["role"] == "client"
    assert "exp" in decoded
    assert "jti" in decoded
    
    # Refresh Token (exp kira 7 dias)
    refresh_token = security.create_refresh_token(data)
    decoded_refresh = security.decode_token(refresh_token)
    assert decoded_refresh["sub"] == user_id
    assert "exp" in decoded_refresh
    assert decoded_refresh["type"] == "refresh"

def test_jwt_token_expiry():
    """Testa se tokens expirados levantam erro."""
    from fastapi import HTTPException
    data = {"sub": "user_id"}
    # Criar token com expiração negativa
    token = security.create_access_token(data, expires_delta=timedelta(seconds=-1))
    with pytest.raises(HTTPException) as exc:
        security.decode_token(token)
    assert exc.value.status_code == 401

def test_lgpd_masking_utilities():
    """Testa utilitários de mascaramento PII."""
    assert lgpd_service.mask_cpf("123.456.789-01") == "***.***.***-01"
    assert lgpd_service.mask_cnpj("12.345.678/0001-90") == "**.***.****/****-90"

@pytest.mark.asyncio
async def test_lgpd_anonymize_user():
    """Testa lógica de anonimização de usuário."""
    # Objeto mockado ou real
    class MockUser:
        id = uuid4()
        name = "João Silva"
        email = "joao@exemplo.com"
        phone = "+5511999999999"
        role = "client"
        
    user = MockUser()
    lgpd_service.anonymize_user_object(user) # Função que altera o objeto in-memory/prepare-for-update
    
    assert user.name == "Usuário removido"
    assert user.email.endswith("@anon.local")
    assert user.phone is None

@pytest.mark.asyncio
async def test_lgpd_check_can_delete_raises_conflict(db_session):
    """Verifica se check_can_delete levanta erro se houver contratos ativos."""
    # Este teste precisaria de dados no banco (User + Contract com status='in_progress')
    # Por enquanto, focamos na estrutura do TDD.
    pass
