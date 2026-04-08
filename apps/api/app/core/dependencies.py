from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as aioredis

from app.core.security import decode_token
from app.core.database import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_tokens_redis(request: Request) -> aioredis.Redis:
    """Retorna o cliente Redis para tokens a partir do app.state (criado no lifespan)."""
    return request.app.state.tokens_redis


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependência para obter o usuário autenticado via JWT."""
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido (sem sub)",
        )
    
    # Buscar usuário no banco
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo",
        )
        
    return user


def require_role(*roles: str):
    """Dependência para exigir roles específicos. Admin sempre tem acesso."""
    def role_checker(user: User = Depends(get_current_user)):
        # Admin bypassa qualquer restrição de role
        role_val = user.role.value if hasattr(user.role, "value") else str(user.role)
        if role_val == "admin":
            return user
        if role_val not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: permissão insuficiente",
            )
        return user
    return role_checker


# Atalhos para roles comuns
require_client = require_role("client")
require_professional = require_role("professional")
require_admin = require_role("admin")
