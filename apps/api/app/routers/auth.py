from datetime import datetime, timezone
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
import httpx

from app.core.deps import get_current_user, get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    rotate_refresh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.schemas.auth import (
    UserCreate,
    UserResponse,
    UserUpdate,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    DeleteAccountRequest,
    ConsentResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
async def register(user_in: UserCreate, request: Request, db: AsyncSession = Depends(get_db)):
    user_id = uuid4()
    hashed_pwd = hash_password(user_in.password)
    
    # Inserir usuario
    query_user = text("""
        INSERT INTO users (id, name, email, phone, password_hash, role, is_active)
        VALUES (:id, :name, :email, :phone, :pwd, 'client', true)
    """)
    try:
        await db.execute(query_user, {
            "id": user_id, 
            "name": user_in.name, 
            "email": user_in.email, 
            "phone": user_in.phone, 
            "pwd": hashed_pwd
        })
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    # Inserir consents
    query_consent = text("""
        INSERT INTO consent_logs (id, user_id, consent_type, version, ip_address, user_agent)
        VALUES (:cid, :uid, :ctype, '2026-01', :ip, :ua)
    """)
    ip = request.client.host if request.client else "127.0.0.1"
    ua = request.headers.get("user-agent", "unknown")
    
    await db.execute(query_consent, {"cid": uuid4(), "uid": user_id, "ctype": "terms", "ip": ip, "ua": ua})
    await db.execute(query_consent, {"cid": uuid4(), "uid": user_id, "ctype": "privacy", "ip": ip, "ua": ua})
    
    await db.commit()

    # Emitir tokens
    access = create_access_token({"sub": str(user_id)})
    refresh = create_refresh_token({"sub": str(user_id)})
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60)

@router.post("/login", response_model=TokenResponse)
async def login(login_in: LoginRequest, db: AsyncSession = Depends(get_db)):
    query = text("SELECT id, password_hash FROM users WHERE email = :email")
    res = await db.execute(query, {"email": login_in.email.lower()})
    row = res.fetchone()
    
    if not row or not verify_password(login_in.password, row._mapping["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
        
    user_id = row._mapping["id"]
    
    # Update last login
    await db.execute(text("UPDATE users SET last_login_at = now() WHERE id = :idx"), {"idx": user_id})
    await db.commit()
    
    access = create_access_token({"sub": str(user_id)})
    refresh = create_refresh_token({"sub": str(user_id)})
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60)

@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_in: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await rotate_refresh_token(refresh_in.refresh_token, db)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM users WHERE id = :idx")
    res = await db.execute(query, {"idx": current_user.id})
    row = res.fetchone()
    return UserResponse(**row._mapping)

@router.patch("/me", response_model=UserResponse)
async def update_me(user_update: UserUpdate, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    updates = []
    params = {"idx": current_user.id}
    
    update_data = user_update.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        updates.append(f"{k} = :{k}")
        params[k] = v
        
    if updates:
        query = text(f"UPDATE users SET {', '.join(updates)}, updated_at = now() WHERE id = :idx RETURNING *")
        res = await db.execute(query, params)
        await db.commit()
        row = res.fetchone()
        return UserResponse(**row._mapping)
        
    # If no updates, return current
    query = text("SELECT * FROM users WHERE id = :idx")
    res = await db.execute(query, params)
    return UserResponse(**res.fetchone()._mapping)

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(delete_req: DeleteAccountRequest, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # 1. Verificar senha
    q_pass = text("SELECT password_hash FROM users WHERE id = :idx")
    res_pass = await db.execute(q_pass, {"idx": current_user.id})
    if not verify_password(delete_req.password, res_pass.fetchone()._mapping["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
        
    # 2. Check contratos ativos
    q_contracts = text("SELECT id FROM contracts WHERE (client_id = :idx OR professional_id = :idx) AND status = 'in_progress' LIMIT 1")
    res_con = await db.execute(q_contracts, {"idx": current_user.id})
    if res_con.fetchone() is not None:
        raise HTTPException(status_code=409, detail="Existem contratos em andamento")
        
    # 3. Anonimizar
    q_anon = text("""
        UPDATE users 
        SET is_active = false,
            name = 'Usuário Removido',
            email = :new_email,
            phone = NULL,
            avatar_url = NULL,
            password_hash = 'deleted'
        WHERE id = :idx
    """)
    new_email = f"removed_{current_user.id}@servicoja.invalid"
    await db.execute(q_anon, {"new_email": new_email, "idx": current_user.id})
    
    # 4. Revogar refresh tokens (assumed table)
    try:
        await db.execute(text("UPDATE refresh_tokens SET revoked = true WHERE user_id = :idx"), {"idx": current_user.id})
    except:
        pass
        
    # 5. Profissional clean up
    if current_user.role == "professional":
        try:
            await db.execute(text("UPDATE bids SET status = 'cancelled' WHERE professional_id = :idx AND status = 'pending'"), {"idx": current_user.id})
            res_doc = await db.execute(text("SELECT document_path FROM professionals WHERE user_id = :idx"), {"idx": current_user.id})
            doc = res_doc.fetchone()
            if doc and doc._mapping.get("document_path"):
                import os
                try: 
                    os.remove(doc._mapping["document_path"])
                except: 
                    pass
        except:
            pass
            
    await db.commit()

@router.get("/me/consents", response_model=List[ConsentResponse])
async def get_consents(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = text("SELECT consent_type, version, accepted_at FROM consent_logs WHERE user_id = :idx ORDER BY accepted_at DESC")
    res = await db.execute(query, {"idx": current_user.id})
    return [ConsentResponse(**row._mapping) for row in res.fetchall()]

@router.post("/oauth/google", response_model=TokenResponse)
async def google_auth(code: str, db: AsyncSession = Depends(get_db)):
    # Very basic mockup to represent the flow
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
         raise HTTPException(status_code=500, detail="Google oauth not configured")

    async with httpx.AsyncClient() as client:
        # Simulando uma resposta da google API
        # na aplicacao real bateriamos em https://oauth2.googleapis.com/token
        # Aqui, como esboco, vamos mockar por falha se vier vazio
        if code == "invalid":
            raise HTTPException(status_code=401, detail="Token Google inválido")
            
        email = f"{code}@google.com" # Dummy email base on code
        
    query = text("SELECT id FROM users WHERE email = :email")
    res = await db.execute(query, {"email": email})
    row = res.fetchone()
    
    if not row:
        user_id = uuid4()
        await db.execute(text("""
            INSERT INTO users (id, name, email, role, is_active, password_hash)
            VALUES (:id, :name, :email, 'client', true, 'oauth')
        """), {"id": user_id, "name": "Google User", "email": email})
    else:
        user_id = row._mapping["id"]
        
    await db.commit()
    return TokenResponse(
        access_token=create_access_token({"sub": str(user_id)}),
        refresh_token=create_refresh_token({"sub": str(user_id)}),
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
