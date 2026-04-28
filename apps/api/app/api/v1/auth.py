from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
import redis.asyncio as aioredis

import httpx
import urllib.parse
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.dependencies import get_current_user, get_tokens_redis, get_db
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
from app.services import lgpd_service

from app.api.v1.deps import get_register_client_use_case, get_login_use_case
from app.application.use_cases.register_client_use_case import RegisterClientUseCase, RegisterClientInput
from app.application.use_cases.login_use_case import LoginUseCase, LoginInput
from app.domain.exceptions import BusinessRuleViolationError, UnauthorizedError

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    request: Request,
    register_use_case: RegisterClientUseCase = Depends(get_register_client_use_case)
):
    """Registra um novo cliente via Use Case."""
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "unknown")
    
    try:
        input_data = RegisterClientInput(
            name=user_in.name,
            email=user_in.email,
            phone=user_in.phone,
            password=user_in.password,
            ip_address=ip,
            user_agent=ua
        )
        user = await register_use_case.execute(input_data)
        
        return TokenResponse(
            access_token=create_access_token({"sub": str(user.id), "role": user.role.value}),
            refresh_token=create_refresh_token({"sub": str(user.id)})
        )
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(
    login_in: LoginRequest,
    login_use_case: LoginUseCase = Depends(get_login_use_case)
):
    """Autentica usuário via Use Case."""
    try:
        input_data = LoginInput(email=login_in.email, password=login_in.password)
        user = await login_use_case.execute(input_data)
        
        return TokenResponse(
            access_token=create_access_token({"sub": str(user.id), "role": user.role.value}),
            refresh_token=create_refresh_token({"sub": str(user.id)})
        )
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    refresh_in: RefreshRequest,
    tokens_redis: aioredis.Redis = Depends(get_tokens_redis)
):
    """Rotaciona o par de tokens (Mantido do core)."""
    payload = decode_token(refresh_in.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token inválido")
    jti = payload.get("jti")
    user_id = payload.get("sub")
    if await is_refresh_token_revoked(jti, tokens_redis):
        raise HTTPException(status_code=401, detail="Token já utilizado")
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
    # db is still needed for core patching if not refactored yet
):
    # This endpoint still uses direct model patching for now as it's a simple CRUD
    # In a full refactor, this would also be a Use Case
    if user_update.name is not None: user.name = user_update.name
    if user_update.phone is not None: user.phone = user_update.phone
    if user_update.avatar_url is not None: user.avatar_url = user_update.avatar_url
    return user

@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_me(
    delete_in: DeleteAccountRequest,
    user: User = Depends(get_current_user),
):
    """Exclusão de conta (Anonimização LGPD)."""
    if not verify_password(delete_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Senha incorreta")
    # LGPD logic remains in service for now
    await lgpd_service.check_can_delete(None, user.id) # Session handle needs fix in service
    lgpd_service.anonymize_user_object(user)
    return {"message": "Conta excluída com sucesso"}

@router.get("/google/login")
async def google_login():
    if settings.ENVIRONMENT == "development" and not settings.GOOGLE_CLIENT_ID:
        # Modo dev: redireciona direto pro callback mockado
        return RedirectResponse("/api/v1/auth/google/callback?code=mock_code")
        
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google oauth not configured")
    
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(code: str, request: Request, db: AsyncSession = Depends(get_db)):
    if settings.ENVIRONMENT == "development" and code == "mock_code":
        email = "test_google@example.com"
        name = "Test Google User"
    else:
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
             raise HTTPException(status_code=500, detail="Google oauth not configured")

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Falha na autenticação social")
            
            token_data = response.json()
            access_token = token_data.get("access_token")

            userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}
            userinfo_response = await client.get(userinfo_url, headers=headers)
            
            if userinfo_response.status_code != 200:
                raise HTTPException(status_code=401, detail="Falha ao obter dados do Google")
                
            userinfo = userinfo_response.json()
            email = userinfo.get("email")
            name = userinfo.get("name", "Google User")
            
            if not email:
                raise HTTPException(status_code=400, detail="Email não retornado pelo Google")
            
    query = text("SELECT id FROM users WHERE email = :email")
    res = await db.execute(query, {"email": email.lower()})
    row = res.fetchone()
    
    if not row:
        user_id = uuid4()
        # Inserir usuario
        await db.execute(text("""
            INSERT INTO users (id, name, email, role, is_active, password_hash)
            VALUES (:id, :name, :email, 'client', true, 'oauth')
        """), {"id": user_id, "name": name, "email": email.lower()})
        
        # Inserir consents (LGPD spec requirement)
        query_consent = text("""
            INSERT INTO consent_logs (id, user_id, consent_type, version, ip_address, user_agent)
            VALUES (:cid, :uid, :ctype, :version, :ip, :ua)
        """)
        ip = request.client.host if request.client else "127.0.0.1"
        ua = request.headers.get("user-agent", "unknown")
        
        await db.execute(query_consent, {"cid": uuid4(), "uid": user_id, "ctype": "terms", "version": settings.TERMS_VERSION, "ip": ip, "ua": ua})
        await db.execute(query_consent, {"cid": uuid4(), "uid": user_id, "ctype": "privacy", "version": settings.TERMS_VERSION, "ip": ip, "ua": ua})
        
    else:
        user_id = row._mapping["id"]
        # Update last login
        await db.execute(text("UPDATE users SET last_login_at = now() WHERE id = :idx"), {"idx": user_id})
        
    await db.commit()
    
    sys_access_token = create_access_token({"sub": str(user_id)})
    sys_refresh_token = create_refresh_token({"sub": str(user_id)})
    
    redirect_url = f"{settings.FRONTEND_AUTH_CALLBACK_URL}?access_token={sys_access_token}&refresh_token={sys_refresh_token}"
    return RedirectResponse(redirect_url)
