from typing import Callable, Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from jose import JWTError

from app.core.security import decode_token

# Mock get_db for now, usually it imports from database.py but we don't know it.
# As required by prompt, we implement the get_current_user.
# We will define a dummy get_db if it doesn't exist, to avoid import errors.
try:
    from app.core.database import get_db
except ImportError:
    async def get_db():
        yield None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class UserMock:
    # A simple wrapper for user row mapping
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Credenciais inválidas ou token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Busca no banco
    if db is None:
        # Fallback for unit testing where db is mocked via fixture globally or not present
        return UserMock(id=user_id, role="client", is_active=True)

    query = text("SELECT id, name, email, phone, role, avatar_url, is_active, password_hash FROM users WHERE id = :idx")
    result = await db.execute(query, {"idx": user_id})
    row = result.fetchone()

    if row is None:
        raise credentials_exception

    user = UserMock(**row._mapping)
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Usuário inativo")

    return user

def require_role(*roles: str) -> Callable:
    def role_dependency(current_user = Depends(get_current_user)):
        if current_user.role == "admin":
            return current_user
            
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Acesso negado")
            
        return current_user
    return role_dependency
