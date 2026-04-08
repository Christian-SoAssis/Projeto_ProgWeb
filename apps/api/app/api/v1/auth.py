from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_tokens_redis
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    is_refresh_token_revoked,
    mark_refresh_token_used,
    verify_password
)
from app.models.user import User, UserRole
from app.schemas.v1.auth import (
    UserCreate,
    UserUpdate,
    UserResponse,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    DeleteAccountRequest
)
from app.schemas.v1.lgpd import ConsentResponse
from app.services import auth_service, lgpd_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Registra um novo cliente e retorna tokens."""
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "unknown")
    
    user = await auth_service.create_user_with_consent(
        db=db,
        user_in=user_in,
        role=UserRole.CLIENT,
        ip_address=ip,
        user_agent=ua
    )
    await db.commit()
    
    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_in: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Autentica usuário e retorna tokens."""
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.email == login_in.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_in.password, user.password_hash) or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    
    # Atualizar last_login_at
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    
    return TokenResponse(
        access_token=create_access_token({"sub": str(user.id), "role": user.role.value}),
        refresh_token=create_refresh_token({"sub": str(user.id)})
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    refresh_in: RefreshRequest,
    tokens_redis: aioredis.Redis = Depends(get_tokens_redis)
):
    """Rotaciona o par de tokens usando refresh token rotation."""
    payload = decode_token(refresh_in.refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token inválido")
        
    jti = payload.get("jti")
    user_id = payload.get("sub")
    
    if await is_refresh_token_revoked(jti, tokens_redis):
        raise HTTPException(status_code=401, detail="Token já utilizado")
        
    # Marcar como usado
    exp = payload.get("exp")
    now_ts = int(datetime.now(timezone.utc).timestamp())
    ttl = max(exp - now_ts, 0)
    await mark_refresh_token_used(jti, ttl, tokens_redis)
    
    return TokenResponse(
        access_token=create_access_token({"sub": user_id, "role": payload.get("role", "client")}),
        refresh_token=create_refresh_token({"sub": user_id, "role": payload.get("role", "client")})
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Retorna dados do usuário autenticado."""
    return user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    user_update: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Atualização parcial do perfil (nome, telefone, avatar)."""
    if user_update.name is not None:
        user.name = user_update.name
    if user_update.phone is not None:
        user.phone = user_update.phone
    if user_update.avatar_url is not None:
        user.avatar_url = user_update.avatar_url
        
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_me(
    delete_in: DeleteAccountRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Exclusão de conta com anonimização (LGPD)."""
    # 1. Verificar senha
    if not verify_password(delete_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Senha incorreta")
    
    # 2. Verificar impedimentos (contratos ativos)
    await lgpd_service.check_can_delete(db, user.id)
    
    # 3. Se profissional, limpar rastro
    if user.role == UserRole.PROFESSIONAL:
        await lgpd_service.cancel_pending_bids(db, user.id)
        await lgpd_service.clear_professional_search_vector(db, user.id)
        await lgpd_service.remove_professional_documents(user.id)
        
    # 4. Anonimizar
    lgpd_service.anonymize_user_object(user)
    
    await db.commit()
    return {"message": "Conta excluída com sucesso"}


@router.get("/me/consents", response_model=List[ConsentResponse])
async def get_my_consents(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lista histórico de consentimentos do usuário."""
    from sqlalchemy import select
    from app.models.lgpd import ConsentLog
    result = await db.execute(
        select(ConsentLog)
        .where(ConsentLog.user_id == user.id)
        .order_by(ConsentLog.accepted_at.desc())
    )
    return result.scalars().all()
