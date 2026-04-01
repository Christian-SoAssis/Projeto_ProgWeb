import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from uuid import uuid4
import bcrypt
from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.redis import tokens_redis

# JWT configuration
SECRET_KEY = settings.JWT_SECRET
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS

def hash_password(plain: str) -> str:
    """Gera hash bcrypt com salt automático."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    """Verifica senha contra hash bcrypt."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um Access Token JWT com claims numéricas (exp, iat)."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "jti": str(uuid4()),
        "type": "access"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Cria um Refresh Token JWT com claims numéricas (exp, iat)."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "jti": str(uuid4()),
        "type": "refresh"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """Decodifica e valida um token JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def is_refresh_token_revoked(jti: str) -> bool:
    """Verifica se o JTI do refresh token está no Redis (revogado ou já usado)."""
    return await tokens_redis.exists(f"rotated:{jti}")

async def mark_refresh_token_used(jti: str, expires_in_seconds: int):
    """Marca um refresh token como usado no Redis para evitar replay attack."""
    await tokens_redis.setex(f"rotated:{jti}", expires_in_seconds, "1")

async def revoke_user_tokens(user_id: str):
    """Revoga todos os tokens de um usuário (em caso de suspeita de breach)."""
    await tokens_redis.setex(f"breach:{user_id}", 3600 * 24, "1")
