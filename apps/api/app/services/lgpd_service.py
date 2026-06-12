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


async def run_data_retention_policy(db: AsyncSession) -> dict:
    """
    Executa a política de retenção de dados da LGPD:
    1. Contas inativas há 12 meses -> Anonimizadas.
    2. Contas inativas há 11 meses (335 dias) -> Notificadas (aviso 30 dias antes).
    3. Conteúdo de mensagens de chat com mais de 24 meses (730 dias) -> Removido.
    4. Notificações com mais de 90 dias -> Removidas (como logs/dados temporários).
    """
    from datetime import datetime, timezone, timedelta
    from sqlalchemy import select, update, delete, text
    from app.models.user import User
    from app.models.notification import Notification

    now = datetime.now(timezone.utc)

    # 1. Notificação de Contas Inativas (11 meses sem login, ou seja, 335 dias)
    warning_threshold = now - timedelta(days=335)
    retention_threshold = now - timedelta(days=365)

    # Buscar usuários elegíveis para aviso:
    # last_login_at < warning_threshold (ou created_at se last_login_at is None)
    # e last_login_at >= retention_threshold (ou created_at se last_login_at is None)
    # e que sejam ativos, e que não sejam admin
    query_warn = select(User).where(
        User.is_active == True,
        User.role != "admin",
        (
            ((User.last_login_at != None) & (User.last_login_at < warning_threshold) & (User.last_login_at >= retention_threshold)) |
            ((User.last_login_at == None) & (User.created_at < warning_threshold) & (User.created_at >= retention_threshold))
        )
    )
    result_warn = await db.execute(query_warn)
    users_to_warn = result_warn.scalars().all()

    warned_count = 0
    for user in users_to_warn:
        # Verificar se já recebeu a notificação nos últimos 30 dias
        check_notification = select(Notification).where(
            Notification.user_id == user.id,
            Notification.type == "account_warning",
            Notification.created_at >= now - timedelta(days=30)
        )
        notif_exists = await db.execute(check_notification)
        if not notif_exists.scalar_one_or_none():
            # Inserir notificação de aviso
            db.add(Notification(
                user_id=user.id,
                type="account_warning",
                payload={
                    "message": "Sua conta está inativa há 11 meses e será anonimizada em 30 dias se você não realizar login.",
                    "type": "inactivity_warning"
                }
            ))
            # Mock de envio de e-mail (imprime no log)
            print(f"[LGPD EMAIL MOCK] Enviando aviso de inatividade para {user.email}")
            warned_count += 1

    # 2. Anonimização de Contas Inativas (12 meses sem login / 365 dias)
    query_anon = select(User).where(
        User.is_active == True,
        User.role != "admin",
        (
            ((User.last_login_at != None) & (User.last_login_at < retention_threshold)) |
            ((User.last_login_at == None) & (User.created_at < retention_threshold))
        )
    )
    result_anon = await db.execute(query_anon)
    users_to_anon = result_anon.scalars().all()

    anon_count = 0
    for user in users_to_anon:
        anonymize_user_object(user)
        # Se for profissional, limpa search_vector, lances e documentos
        role_val = user.role.value if hasattr(user.role, "value") else str(user.role)
        if role_val == "professional":
            await clear_professional_search_vector(db, user.id)
            await cancel_pending_bids(db, user.id)
            await remove_professional_documents(user.id)
        anon_count += 1
        print(f"[LGPD COMPLIANCE] Conta {user.id} anonimizada por inatividade de 12 meses.")

    # 3. Remover conteúdo de mensagens com mais de 24 meses (730 dias)
    msg_threshold = now - timedelta(days=730)
    result_msg = await db.execute(
        text("UPDATE messages SET content = '[REMOVED]' WHERE created_at < :t AND content != '[REMOVED]'"),
        {"t": msg_threshold}
    )
    msg_purged = result_msg.rowcount

    # 4. Remover notificações com mais de 90 dias
    notif_threshold = now - timedelta(days=90)
    result_notif = await db.execute(
        delete(Notification).where(Notification.created_at < notif_threshold)
    )
    notif_purged = result_notif.rowcount

    await db.flush()

    return {
        "warned_count": warned_count,
        "anon_count": anon_count,
        "messages_purged_count": msg_purged,
        "notifications_purged_count": notif_purged
    }
