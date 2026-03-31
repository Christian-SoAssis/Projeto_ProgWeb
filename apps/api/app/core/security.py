import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from uuid import uuid4

import bcrypt
from jose import JWTError, jwt
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.schemas.auth import TokenResponse

SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Bycrypt configuration for password hashing
# using raw python bcrypt
def hash_password(plain: str) -> str:
    # rounds=12 is standard, bcrypt module determines default usually 12
    # passlib is also available in requirements: `passlib[bcrypt]`
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "jti": str(uuid4())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode.update({"type": "refresh"})
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "jti": str(uuid4())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

async def rotate_refresh_token(old_token: str, db: AsyncSession) -> TokenResponse:
    # 1. Validar e decodificar o token antigo
    try:
        payload = decode_token(old_token)
        if payload.get("type") != "refresh":
             raise HTTPException(status_code=401, detail="Token não é do tipo refresh.")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token inválido ou expirado.")

    if not user_id:
        raise HTTPException(status_code=401, detail="Refresh token inválido (sem sub).")

    # 2. Verificar se o token já foi revogado no banco
    q_check = text("SELECT revoked FROM refresh_tokens WHERE token = :token")
    res = await db.execute(q_check, {"token": old_token})
    row = res.fetchone()
    if row and row._mapping["revoked"]:
        raise HTTPException(status_code=401, detail="Refresh token já utilizado ou revogado.")

    # 3. Buscar role do usuário para incluir no novo access_token
    res_user = await db.execute(text("SELECT role FROM users WHERE id = :uid"), {"uid": user_id})
    user_row = res_user.fetchone()
    if not user_row:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    role = user_row._mapping["role"]

    # 4. Registrar revogação do token atual
    # Para simplicidade e eficácia: se não existe na tabela, insere como revogado. Se existe, marca.
    query_revoke = text("""
        INSERT INTO refresh_tokens (token, user_id, revoked, expires_at)
        VALUES (:token, :uid, true, :exp)
        ON CONFLICT (token) DO UPDATE SET revoked = true
    """)
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    await db.execute(query_revoke, {"token": old_token, "uid": user_id, "exp": expires_at})
    await db.commit()

    # 5. Emitir novo par de tokens
    new_access = create_access_token({"sub": user_id, "role": role})
    new_refresh = create_refresh_token({"sub": user_id})

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
