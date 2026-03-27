"""
Utilitários de autenticação:
- Hash/verificação de senha com bcrypt
- Geração e validação de JWT (access + refresh tokens)
- Rotação de refresh token (7 dias)
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Contexto bcrypt para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


# ─── Senha ────────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Gera hash bcrypt da senha."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica senha contra hash bcrypt."""
    return pwd_context.verify(plain, hashed)


# ─── JWT ──────────────────────────────────────────────────────────────────────

def _create_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    """Cria um JWT assinado com o secret e o algoritmo HS256."""
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + expires_delta
    payload["iat"] = datetime.now(timezone.utc)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def create_access_token(user_id: str, role: str) -> str:
    """Gera access token com expiração de JWT_ACCESS_TOKEN_EXPIRE_MINUTES."""
    return _create_token(
        {"sub": user_id, "role": role, "type": "access"},
        timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: str) -> str:
    """Gera refresh token com expiração de JWT_REFRESH_TOKEN_EXPIRE_DAYS."""
    return _create_token(
        {"sub": user_id, "type": "refresh"},
        timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    Decodifica e valida um JWT.
    Levanta JWTError se inválido ou expirado.
    """
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
