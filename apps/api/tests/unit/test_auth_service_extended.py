import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.services.auth_service import build_professional, create_user_with_consent
from app.schemas.v1.auth import ProfessionalCreate, UserCreate
from app.models.user import User, UserRole

@pytest.mark.asyncio
async def test_build_professional_success(db_session: AsyncSession):
    """Testa criação de profissional com sucesso (DB + Mock IO)."""
    # Criar usuário real para evitar IntegrityError de FK
    user = User(
        name="Prof User",
        email=f"prof_{uuid4()}@example.com",
        password_hash="hash",
        role=UserRole.PROFESSIONAL,
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    
    user_id = user.id
    prof_in = ProfessionalCreate(
        bio="Profissional experiente em encanamento e eletricidade.",
        latitude=-23.5505,
        longitude=-46.6333,
        service_radius_km=25.0,
        hourly_rate_cents=12000,
        category_ids=[uuid4()],
        document_type="cpf"
    )
    
    # Mock do arquivo
    mock_file = MagicMock(spec=UploadFile)
    mock_file.content_type = "application/pdf"
    mock_file.filename = "doc.pdf"
    mock_file.file = MagicMock()
    
    with patch("os.makedirs"), \
         patch("shutil.copyfileobj"), \
         patch("builtins.open", MagicMock()):
        
        prof = await build_professional(db_session, user_id, prof_in, mock_file)
        
        assert prof.user_id == user_id
        assert prof.bio == prof_in.bio
        assert prof.is_verified is False
        assert prof.document_path is not None
        assert "verification_doc.pdf" in prof.document_path

@pytest.mark.asyncio
async def test_build_professional_invalid_type(db_session: AsyncSession):
    """Testa erro de tipo de arquivo não suportado."""
    user_id = uuid4()
    prof_in = ProfessionalCreate(
        bio="Bio válida suficiente.",
        latitude=0,
        longitude=0,
        service_radius_km=10,
        hourly_rate_cents=1000,
        category_ids=[uuid4()],
        document_type="cpf"
    )
    
    mock_file = MagicMock(spec=UploadFile)
    mock_file.content_type = "text/plain" # Inválido
    
    with pytest.raises(HTTPException) as exc:
        await build_professional(db_session, user_id, prof_in, mock_file)
    assert exc.value.status_code == 415

@pytest.mark.asyncio
async def test_build_professional_storage_error(db_session: AsyncSession):
    """Testa erro de IO no storage."""
    # Criar usuário real para evitar IntegrityError de FK antes da falha de IO
    user = User(
        name="Prof User IO",
        email=f"prof_io_{uuid4()}@example.com",
        password_hash="hash",
        role=UserRole.PROFESSIONAL,
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()

    user_id = user.id
    prof_in = ProfessionalCreate(
        bio="Bio válida suficiente.",
        latitude=0,
        longitude=0,
        service_radius_km=10,
        hourly_rate_cents=1000,
        category_ids=[uuid4()],
        document_type="cpf"
    )
    
    mock_file = MagicMock(spec=UploadFile)
    mock_file.content_type = "application/pdf"
    mock_file.filename = "doc.pdf"
    
    with patch("os.makedirs"), \
         patch("builtins.open", side_effect=Exception("Disk full")):
        
        with pytest.raises(HTTPException) as exc:
            await build_professional(db_session, user_id, prof_in, mock_file)
        assert exc.value.status_code == 500
        assert "Disk full" in exc.value.detail

@pytest.mark.asyncio
async def test_create_user_with_consent_success(db_session: AsyncSession):
    """Testa criação de usuário com consentimento (fluxo feliz)."""
    email = f"success_{uuid4()}@example.com"
    user_in = UserCreate(
        name="Happy User",
        email=email,
        password="password123",
        consent_terms=True,
        consent_privacy=True
    )
    
    user = await create_user_with_consent(db_session, user_in)
    await db_session.flush()
    
    assert user.email == email
    assert user.name == "Happy User"
    assert user.is_active is True
    
    # Verificar se logs de consentimento foram criados
    from app.models.lgpd import ConsentLog
    from sqlalchemy import select
    res = await db_session.execute(select(ConsentLog).where(ConsentLog.user_id == user.id))
    logs = res.scalars().all()
    assert len(logs) == 2
    types = [l.consent_type for l in logs]
    assert "terms" in types
    assert "privacy" in types

@pytest.mark.asyncio
async def test_create_user_with_consent_duplicate_email(db_session: AsyncSession):
    """Testa falha ao criar usuário com e-mail duplicado."""
    email = f"duplicate_{uuid4()}@example.com"
    user_in = UserCreate(
        name="User 1",
        email=email,
        password="password123",
        consent_terms=True,
        consent_privacy=True
    )
    
    # Cria o primeiro usuário manualmente para garantir que está no banco
    user1 = User(
        name="User 1",
        email=email,
        password_hash="hash",
        role=UserRole.CLIENT,
        is_active=True
    )
    db_session.add(user1)
    await db_session.flush()
        
    # Tenta criar o segundo com mesmo e-mail via service
    user_in_2 = UserCreate(
        name="User 2",
        email=email,
        password="otherpassword",
        consent_terms=True,
        consent_privacy=True
    )
    
    with pytest.raises(HTTPException) as exc:
        await create_user_with_consent(db_session, user_in_2)
    assert exc.value.status_code == 409
    assert "já cadastrado" in exc.value.detail
