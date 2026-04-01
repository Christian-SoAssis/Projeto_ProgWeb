import os
import shutil
import uuid
from uuid import UUID
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import hash_password
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.professional import Professional
from app.models.lgpd import ConsentLog
from app.schemas.v1.auth import UserCreate, ProfessionalCreate

async def create_user_with_consent(
    db: AsyncSession, 
    user_in: UserCreate, 
    role: UserRole = UserRole.CLIENT,
    ip_address: str = None,
    user_agent: str = None
) -> User:
    """Cria um usuário e registra logs de consentimento na mesma transação."""
    # Verificar se email já existe
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado"
        )
    
    # Criar user
    user = User(
        name=user_in.name,
        email=user_in.email,
        phone=user_in.phone,
        password_hash=hash_password(user_in.password),
        role=role,
        is_active=True
    )
    db.add(user)
    await db.flush() # Gerar ID do usuário
    
    # Registrar consentimentos
    consents = [
        ConsentLog(
            user_id=user.id,
            consent_type="terms",
            version=settings.TERMS_VERSION,
            ip_address=ip_address,
            user_agent=user_agent
        ),
        ConsentLog(
            user_id=user.id,
            consent_type="privacy",
            version=settings.TERMS_VERSION,
            ip_address=ip_address,
            user_agent=user_agent
        )
    ]
    db.add_all(consents)
    
    return user

async def build_professional(
    db: AsyncSession,
    user_id: UUID,
    prof_in: ProfessionalCreate,
    document: UploadFile
) -> Professional:
    """Cria o perfil profissional e salva o documento fisicamente."""
    # 1. Validar documento
    if document.content_type not in ["application/pdf", "image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Apenas PDF, JPG e PNG são permitidos"
        )
    
    # 2. Criar registro no banco
    professional = Professional(
        user_id=user_id,
        bio=prof_in.bio,
        latitude=prof_in.latitude,
        longitude=prof_in.longitude,
        service_radius_km=prof_in.service_radius_km,
        hourly_rate_cents=prof_in.hourly_rate_cents,
        document_type=prof_in.document_type,
        is_verified=False
    )
    db.add(professional)
    await db.flush() # Gerar ID do profissional
    
    # 3. Salvar arquivo fisicamente
    # Path: ./uploads/documents/{user_id}/{filename}
    doc_dir = os.path.join(settings.UPLOADS_DIR, "documents", str(user_id))
    os.makedirs(doc_dir, exist_ok=True)
    
    file_ext = os.path.splitext(document.filename)[1]
    file_path = os.path.join(doc_dir, f"verification_doc{file_ext}")
    
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(document.file, f)
        professional.document_path = file_path
    except Exception as e:
        # Se falhar o IO, a transação do banco fará rollback no router (commit final)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao salvar documento: {str(e)}"
        )
        
    return professional
