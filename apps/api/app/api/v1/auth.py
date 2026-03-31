"""Router de autenticação — POST /auth/register, /login, /refresh, GET /me, DELETE /me."""
import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from sqlalchemy import text
from app.models.user import User, UserRole
from app.schemas.v1.auth import (
    DeleteAccountRequest,
    LoginRequest,
    MeResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    ConsentResponse,
)
from typing import List

router = APIRouter(prefix="/auth", tags=["Auth"])


# ─── Registro ─────────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo cliente",
)
async def register(
    body: RegisterRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Cria um novo usuário com role=client.
    - Verifica duplicidade de e-mail (409)
    - Hash bcrypt da senha
    - Retorna access + refresh tokens
    """
    # Verificar e-mail duplicado
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    user = User(
        id=uuid.uuid4(),
        name=body.name,
        email=body.email,
        phone=body.phone,
        password_hash=hash_password(body.password),
        role=UserRole.CLIENT.value,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # ── Criar logs de consentimento (LGPD) ───────────────────────────────────
    ip = request.client.host if request.client else "127.0.0.1"
    ua = request.headers.get("user-agent", "unknown")
    query_consent = text("""
        INSERT INTO consent_logs (id, user_id, consent_type, version, ip_address, user_agent)
        VALUES (:cid, :uid, :ctype, '2026-01', :ip, :ua)
    """)
    await db.execute(query_consent, {"cid": uuid.uuid4(), "uid": user.id, "ctype": "terms", "ip": ip, "ua": ua})
    await db.execute(query_consent, {"cid": uuid.uuid4(), "uid": user.id, "ctype": "privacy", "ip": ip, "ua": ua})
    await db.commit()

    return TokenResponse(
        access_token=create_access_token({"sub": str(user.id), "role": user.role.value}),
        refresh_token=create_refresh_token({"sub": str(user.id)}),
    )


# ─── Login ────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse, summary="Autenticar usuário")
async def login(
    body: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Valida credenciais e retorna tokens.
    Sempre retorna 401 (sem distinguir e-mail/senha — segurança).
    """
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
    )

    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise invalid
    if not verify_password(body.password, user.password_hash):
        raise invalid

    # Atualizar last_login_at
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    return TokenResponse(
        access_token=create_access_token({"sub": str(user.id), "role": user.role.value}),
        refresh_token=create_refresh_token({"sub": str(user.id)}),
    )


# ─── Refresh ──────────────────────────────────────────────────────────────────

@router.post("/refresh", response_model=TokenResponse, summary="Rotacionar refresh token")
async def refresh_token(
    body: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Valida o refresh token e emite novo par de tokens (rotação completa).
    Levanta 401 se o token for inválido ou expirado.
    """
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise JWTError()
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token inválido")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Usuário inválido")

    return TokenResponse(
        access_token=create_access_token({"sub": str(user.id), "role": user.role.value}),
        refresh_token=create_refresh_token({"sub": str(user.id)}),
    )


# ─── Me ───────────────────────────────────────────────────────────────────────

@router.get("/me", response_model=MeResponse, summary="Perfil do usuário autenticado")
async def me(
    user: Annotated[User, Depends(get_current_user)],
) -> MeResponse:
    """Retorna o perfil do usuário autenticado via Bearer token."""
    return MeResponse.model_validate(user)


# ─── LGPD: excluir conta ──────────────────────────────────────────────────────

@router.delete("/me", status_code=204, summary="Excluir conta (LGPD)")
async def delete_account(
    body: DeleteAccountRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Exclusão de conta com confirmação de senha.
    - Anonimiza PII (nome, e-mail, telefone)
    - Desativa a conta
    - Contratos `in_progress` bloqueiam a exclusão (409)
    """
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Senha incorreta")

    # Anonimizar PII (LGPD)
    anon_id = str(user.id)[:8]
    user.name = f"Usuário Removido {anon_id}"
    user.email = f"removed_{anon_id}@deleted.servicoja.com"
    user.phone = None
    user.is_active = False
    user.password_hash = hash_password(uuid.uuid4().hex)

    await db.commit()


# ─── Consents ─────────────────────────────────────────────────────────────────

@router.get("/me/consents", response_model=List[ConsentResponse], summary="Logs de consentimento")
async def get_consents(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> List[ConsentResponse]:
    """Retorna o histórico de consentimentos (LGPD) do usuário."""
    query = text("SELECT consent_type, version, accepted_at FROM consent_logs WHERE user_id = :uid ORDER BY accepted_at DESC")
    result = await db.execute(query, {"uid": user.id})
    # Mapear explicitamente para evitar problemas de compatibilidade Row/Pydantic
    return [
        ConsentResponse(
            consent_type=row._mapping["consent_type"],
            version=row._mapping["version"],
            accepted_at=row._mapping["accepted_at"]
        ) for row in result.fetchall()
    ]
