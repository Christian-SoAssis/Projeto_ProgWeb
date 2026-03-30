import os
import json
from uuid import uuid4
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import ValidationError

from app.core.deps import get_current_user, get_db, require_role
from app.core.security import hash_password
from app.schemas.auth import ProfessionalCreate, ProfessionalResponse

router = APIRouter(prefix="/professionals", tags=["professionals"])

UPLOAD_DIR = "./uploads/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=ProfessionalResponse)
async def register_professional(
    request: Request,
    payload: str = Form(...),
    document_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        data_dict = json.loads(payload)
        user_in = ProfessionalCreate(**data_dict)
    except (json.JSONDecodeError, ValidationError) as e:
        raise HTTPException(status_code=422, detail=str(e))

    user_id = uuid4()
    prof_id = uuid4()
    
    # Check email duplicate
    res_email = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": user_in.email.lower()})
    if res_email.fetchone():
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    # 1. Create User
    await db.execute(
        text("""
            INSERT INTO users (id, name, email, phone, password_hash, role, is_active)
            VALUES (:id, :name, :email, :phone, :pwd, 'professional', true)
        """),
        {
            "id": user_id,
            "name": user_in.name,
            "email": user_in.email,
            "phone": user_in.phone,
            "pwd": hash_password(user_in.password),
        }
    )

    # 2. Save Document File
    user_upload_dir = os.path.join(UPLOAD_DIR, str(user_id))
    os.makedirs(user_upload_dir, exist_ok=True)
    file_path = os.path.join(user_upload_dir, document_file.filename)
    
    with open(file_path, "wb") as f:
        f.write(await document_file.read())

    # 3. Create Professional
    # Using WKTElement equivalent: ST_GeomFromText 
    await db.execute(
        text("""
            INSERT INTO professionals (
                id, user_id, bio, location, service_radius_km, 
                hourly_rate_cents, is_verified, document_path, document_type
            )
            VALUES (
                :pid, :uid, :bio, 
                ST_GeomFromText(:pt, 4326), 
                :radius, :rate, false, :doc_path, :doc_type
            )
        """),
        {
            "pid": prof_id,
            "uid": user_id,
            "bio": user_in.bio,
            "pt": f"POINT({user_in.longitude} {user_in.latitude})",
            "radius": user_in.service_radius_km,
            "rate": user_in.hourly_rate_cents,
            "doc_path": file_path,
            "doc_type": user_in.document_type
        }
    )

    # 4. Consent logs
    ip = request.client.host if request.client else "127.0.0.1"
    ua = request.headers.get("user-agent", "unknown")
    for ctype in ["terms", "privacy"]:
        await db.execute(
            text("INSERT INTO consent_logs (id, user_id, consent_type, version, ip_address, user_agent) VALUES (:cid, :uid, :type, '2026-01', :ip, :ua)"),
            {"cid": uuid4(), "uid": user_id, "type": ctype, "ip": ip, "ua": ua}
        )

    # 5. Professional Categories
    for cat_id in user_in.category_ids:
        await db.execute(
            text("INSERT INTO professional_categories (professional_id, category_id) VALUES (:pid, :cid) ON CONFLICT DO NOTHING"),
            {"pid": prof_id, "cid": str(cat_id)}
        )

    await db.commit()

    # Build Response
    q = text("""
        SELECT u.id, u.name, u.email, u.phone, u.role, u.is_active, u.created_at, u.updated_at,
               p.bio, ST_X(p.location::geometry) as longitude, ST_Y(p.location::geometry) as latitude,
               p.service_radius_km, p.hourly_rate_cents, p.is_verified, p.verified_at, p.reputation_score
        FROM users u
        JOIN professionals p ON u.id = p.user_id
        WHERE u.id = :uid
    """)
    res = await db.execute(q, {"uid": user_id})
    row = res.fetchone()
    
    # Mapeando categorias vazias
    row_dict = dict(row._mapping)
    row_dict["categories"] = []  # O escopo pediria JOIN real pra preencher models

    return ProfessionalResponse(**row_dict)

@router.patch("/admin/{prof_id}", response_model=ProfessionalResponse)
async def approve_professional(
    prof_id: str,
    admin_user = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    # Setar is_verified=True, verified_at=now()
    q_upd = text("""
        UPDATE professionals 
        SET is_verified = true, verified_at = now() 
        WHERE id = :pid OR user_id = :pid
        RETURNING user_id
    """)
    res = await db.execute(q_upd, {"pid": prof_id})
    row = res.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
        
    await db.commit()
    
    # Query e build o response de volta
    q = text("""
        SELECT u.id, u.name, u.email, u.phone, u.role, u.is_active, u.created_at, u.updated_at,
               p.bio, ST_X(p.location::geometry) as longitude, ST_Y(p.location::geometry) as latitude,
               p.service_radius_km, p.hourly_rate_cents, p.is_verified, p.verified_at, p.reputation_score
        FROM users u
        JOIN professionals p ON u.id = p.user_id
        WHERE u.id = :uid
    """)
    res_prof = await db.execute(q, {"uid": row._mapping["user_id"]})
    prof_row = dict(res_prof.fetchone()._mapping)
    prof_row["categories"] = []
    
    return ProfessionalResponse(**prof_row)
