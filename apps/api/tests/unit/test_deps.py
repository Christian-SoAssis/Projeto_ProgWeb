import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from jose import JWTError
from app.core.deps import get_current_user, require_role, UserMock

@pytest.mark.asyncio
async def test_get_current_user_valid_db_none():
    """Testa fallback quando db é None (cenário comum em testes unitários)."""
    token = "valid_token"
    user_id = "test-user-id"
    payload = {"sub": user_id}
    
    with patch("app.core.deps.decode_token", return_value=payload):
        user = await get_current_user(token=token, db=None)
        assert user.id == user_id
        assert user.role == "client"
        assert user.is_active is True

@pytest.mark.asyncio
async def test_get_current_user_valid_with_db():
    """Testa busca no banco quando db é fornecido."""
    token = "valid_token"
    user_id = "test-user-id"
    payload = {"sub": user_id}
    
    db = AsyncMock()
    mock_row = MagicMock()
    # Simula o _mapping retornado pelo SQLAlchemy row
    mock_row._mapping = {
        "id": user_id,
        "name": "Test User",
        "email": "test@example.com",
        "role": "professional",
        "is_active": True
    }
    
    mock_result = MagicMock()
    mock_result.fetchone.return_value = mock_row
    db.execute.return_value = mock_result
    
    with patch("app.core.deps.decode_token", return_value=payload):
        user = await get_current_user(token=token, db=db)
        assert user.id == user_id
        assert user.role == "professional"
        db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_current_user_user_not_found():
    """Testa erro quando usuário não existe no banco."""
    token = "valid_token"
    payload = {"sub": "non-existent"}
    
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None
    db.execute.return_value = mock_result
    
    with patch("app.core.deps.decode_token", return_value=payload):
        with pytest.raises(HTTPException) as exc:
            await get_current_user(token=token, db=db)
        assert exc.value.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_inactive():
    """Testa erro para usuário inativo."""
    token = "valid_token"
    user_id = "inactive-id"
    payload = {"sub": user_id}
    
    db = AsyncMock()
    mock_row = MagicMock()
    mock_row._mapping = {"id": user_id, "role": "client", "is_active": False}
    mock_result = MagicMock()
    mock_result.fetchone.return_value = mock_row
    db.execute.return_value = mock_result
    
    with patch("app.core.deps.decode_token", return_value=payload):
        with pytest.raises(HTTPException) as exc:
            await get_current_user(token=token, db=db)
        assert exc.value.status_code == 401
        assert "inativo" in exc.value.detail.lower()

@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    """Testa token inválido (JWTError)."""
    with patch("app.core.deps.decode_token", side_effect=JWTError):
        with pytest.raises(HTTPException) as exc:
            await get_current_user(token="invalid")
        assert exc.value.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_missing_sub():
    """Testa payload sem o campo 'sub'."""
    with patch("app.core.deps.decode_token", return_value={}):
        with pytest.raises(HTTPException) as exc:
            await get_current_user(token="token")
        assert exc.value.status_code == 401

def test_require_role_admin_bypass():
    """Verifica que admin passa por qualquer role exigida."""
    user = UserMock(role="admin")
    dep = require_role("professional", "client")
    # require_role retorna uma função que espera current_user
    result = dep(current_user=user)
    assert result == user

def test_require_role_success():
    """Verifica que usuário com role correto passa."""
    user = UserMock(role="professional")
    dep = require_role("professional", "client")
    result = dep(current_user=user)
    assert result == user

def test_require_role_forbidden():
    """Verifica acesso negado para role incorreto."""
    user = UserMock(role="client")
    dep = require_role("admin", "professional")
    with pytest.raises(HTTPException) as exc:
        dep(current_user=user)
    assert exc.value.status_code == 403
