import os
import shutil
from uuid import UUID, uuid4
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.models.user import User
from app.models.professional import Professional
from app.models.contract import Contract
from app.models.bid import Bid
from app.core.config import settings

def mask_cpf(cpf: str) -> str:
    """Mascarar CPF: 123.456.789-01 -> ***.***.***-01"""
    if not cpf or len(cpf) < 14:
        return cpf
    return "***.***.***-" + cpf[-2:]

def mask_cnpj(cnpj: str) -> str:
    """Mascarar CNPJ: 12.345.678/0001-90 -> **.***.****/****-90"""
    if not cnpj or len(cnpj) < 18:
        return cnpj
    return "**.***.****/****-" + cnpj[-2:]

async def check_can_delete(db: AsyncSession, user_id: UUID) -> None:
    """Levanta 409 Conflict se o usuário tiver contratos em andamento."""
    # Verificar como cliente ou como profissional
    query = select(Contract).where(
        ((Contract.client_id == user_id) | (Contract.professional_id == 
            select(Professional.id).where(Professional.user_id == user_id).scalar_subquery())),
        Contract.status == "active"
    )
    result = await db.execute(query)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir a conta com contratos em andamento."
        )

def anonymize_user_object(user: User) -> None:
    """Aplica anoninização no objeto User (PII removal)."""
    user.name = "Usuário removido"
    user.email = f"{uuid4()}@anon.local"
    user.phone = None
    user.avatar_url = None
    user.is_active = False

async def clear_professional_search_vector(db: AsyncSession, user_id: UUID) -> None:
    """Limpa o search_vector do profissional para removê-lo das buscas."""
    await db.execute(
        update(Professional)
        .where(Professional.user_id == user_id)
        .values(search_vector=None)
    )

async def cancel_pending_bids(db: AsyncSession, user_id: UUID) -> None:
    """Cancela todos os lances pendentes do profissional."""
    # Primeiro encontrar o ID do profissional
    prof_res = await db.execute(select(Professional.id).where(Professional.user_id == user_id))
    prof_id = prof_res.scalar_one_or_none()
    
    if prof_id:
        await db.execute(
            update(Bid)
            .where(Bid.professional_id == prof_id, Bid.status == "pending")
            .values(status="cancelled")
        )

async def remove_professional_documents(user_id: UUID) -> None:
    """Remove fisicamente os documentos do profissional do filesystem."""
    doc_dir = os.path.join(settings.UPLOADS_DIR, "documents", str(user_id))
    if os.path.exists(doc_dir):
        try:
            shutil.rmtree(doc_dir)
        except Exception:
            # Logar falha mas não interromper fluxo de exclusão
            pass
