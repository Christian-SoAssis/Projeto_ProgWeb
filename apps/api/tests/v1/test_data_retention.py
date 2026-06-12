import os
import pytest
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, text
from app.models.user import User, UserRole
from app.models.professional import Professional
from app.models.bid import Bid
from app.models.category import Category
from app.models.request import Request
from app.models.contract import Contract
from app.models.notification import Notification
from app.services.lgpd_service import run_data_retention_policy
from app.core.config import settings
from geoalchemy2 import WKTElement


@pytest.fixture(scope="function")
async def seed_retention_data(db_session):
    now = datetime.now(timezone.utc)
    
    # 1. Categoria, Request e Bids para testar cancelamento de Bids do profissional inativo
    cat = Category(
        name="Reparos Gerais",
        slug=f"rep_{uuid.uuid4().hex[:4]}",
        color="#112233"
    )
    db_session.add(cat)
    await db_session.flush()

    client_user = User(
        email=f"client_{uuid.uuid4().hex[:6]}@test.com",
        name="Client Active",
        password_hash="hash",
        role=UserRole.CLIENT,
        is_active=True,
        last_login_at=now
    )
    db_session.add(client_user)
    await db_session.flush()

    req = Request(
        client_id=client_user.id,
        category_id=cat.id,
        title="Reparo simples",
        urgency="immediate",
        location=WKTElement("POINT(-45.42 -21.55)", srid=4326),
        status="open"
    )
    db_session.add(req)
    await db_session.flush()

    # 2. Usuários
    # U1: Inativo há 13 meses (Anonimização)
    u_anon = User(
        email="inactive_13m@test.com",
        name="Inactive User 13m",
        password_hash="hash",
        role=UserRole.CLIENT,
        is_active=True,
        last_login_at=now - timedelta(days=395),  # 13 meses
        created_at=now - timedelta(days=400)
    )
    
    # U2: Inativo há 11.5 meses (Aviso)
    u_warn = User(
        email="inactive_11m@test.com",
        name="Inactive User 11m",
        password_hash="hash",
        role=UserRole.CLIENT,
        is_active=True,
        last_login_at=now - timedelta(days=345),  # 11.5 meses
        created_at=now - timedelta(days=350)
    )
    
    # U3: Ativo recentemente (Sem alteração)
    u_active = User(
        email="active_2m@test.com",
        name="Active User 2m",
        password_hash="hash",
        role=UserRole.CLIENT,
        is_active=True,
        last_login_at=now - timedelta(days=60),  # 2 meses
        created_at=now - timedelta(days=70)
    )
    
    # U4: Admin inativo (Sem alteração)
    u_admin = User(
        email="admin_inactive@test.com",
        name="Admin Inactive",
        password_hash="hash",
        role=UserRole.ADMIN,
        is_active=True,
        last_login_at=now - timedelta(days=395),  # 13 meses
        created_at=now - timedelta(days=400)
    )
    
    # U5: Profissional Inativo há 13 meses (Anonimização + Limpar search_vector, bids, documentos)
    u_prof = User(
        email="prof_inactive@test.com",
        name="Professional Inactive",
        password_hash="hash",
        role=UserRole.PROFESSIONAL,
        is_active=True,
        last_login_at=now - timedelta(days=395),
        created_at=now - timedelta(days=400)
    )
    
    db_session.add_all([u_anon, u_warn, u_active, u_admin, u_prof])
    await db_session.flush()

    # Criar Professional record
    prof = Professional(
        user_id=u_prof.id,
        bio="Profissional inativo",
        latitude=-21.55, longitude=-45.42,
        service_radius_km=15.0,
        hourly_rate_cents=6000,
        is_verified=True,
        document_type="cpf"
    )
    db_session.add(prof)
    await db_session.flush()

    # Criar bid pendente do profissional inativo (deve ser cancelado)
    bid = Bid(
        request_id=req.id,
        professional_id=prof.id,
        price_cents=5000,
        message="Eu posso fazer isso",
        status="pending"
    )
    db_session.add(bid)

    # Criar um Contrato ativo para associar as mensagens do chat (ignora validações complexas e FK)
    contract = Contract(
        request_id=req.id,
        professional_id=prof.id,
        client_id=client_user.id,
        agreed_cents=10000,
        status="active"
    )
    db_session.add(contract)
    await db_session.flush()

    # 3. Criar arquivos de documentos do profissional fake
    doc_dir = os.path.join(settings.UPLOADS_DIR, "documents", str(u_prof.id))
    os.makedirs(doc_dir, exist_ok=True)
    doc_file = os.path.join(doc_dir, "cpf.pdf")
    with open(doc_file, "w") as f:
        f.write("mock content")

    # 4. Mensagens vinculadas ao contrato criado
    # Inserir usando SQL direto porque não há modelo SQLAlchemy
    # M1: Antiga (25 meses)
    m1_id = uuid.uuid4()
    await db_session.execute(
        text("""
            INSERT INTO messages (id, contract_id, sender_id, content, created_at)
            VALUES (:id, :contract_id, :sender_id, :content, :created_at)
        """),
        {
            "id": m1_id,
            "contract_id": contract.id,
            "sender_id": client_user.id,
            "content": "Mensagem secreta de 2 anos atrás",
            "created_at": now - timedelta(days=750)
        }
    )
    # M2: Nova (23 meses)
    m2_id = uuid.uuid4()
    await db_session.execute(
        text("""
            INSERT INTO messages (id, contract_id, sender_id, content, created_at)
            VALUES (:id, :contract_id, :sender_id, :content, :created_at)
        """),
        {
            "id": m2_id,
            "contract_id": contract.id,
            "sender_id": client_user.id,
            "content": "Mensagem recente",
            "created_at": now - timedelta(days=690)
        }
    )

    # 5. Notificações
    # N1: Antiga (95 dias)
    n_old = Notification(
        user_id=client_user.id,
        type="new_message",
        payload={"message": "Você tem nova mensagem"},
        created_at=now - timedelta(days=95)
    )
    # N2: Nova (85 dias)
    n_new = Notification(
        user_id=client_user.id,
        type="new_message",
        payload={"message": "Outra mensagem"},
        created_at=now - timedelta(days=85)
    )
    db_session.add_all([n_old, n_new])
    await db_session.flush()

    return {
        "u_anon_id": u_anon.id,
        "u_warn_id": u_warn.id,
        "u_active_id": u_active.id,
        "u_admin_id": u_admin.id,
        "u_prof_id": u_prof.id,
        "prof_id": prof.id,
        "bid_id": bid.id,
        "m1_id": m1_id,
        "m2_id": m2_id,
        "n_old_id": n_old.id,
        "n_new_id": n_new.id,
        "doc_file": doc_file,
        "doc_dir": doc_dir
    }


@pytest.mark.asyncio
async def test_lgpd_data_retention_policy(db_session, seed_retention_data: dict):
    setup = seed_retention_data

    # Executar a política de retenção
    stats = await run_data_retention_policy(db_session)
    await db_session.flush()

    # 1. Verificar estatísticas retornadas
    assert stats["anon_count"] == 2  # u_anon + u_prof
    assert stats["warned_count"] == 1  # u_warn
    assert stats["messages_purged_count"] == 1  # m1
    assert stats["notifications_purged_count"] == 1  # n_old

    # 2. Verificar U1 (u_anon): Deve estar anonimizado e inativo
    res_anon = await db_session.execute(select(User).where(User.id == setup["u_anon_id"]))
    u_anon = res_anon.scalar_one()
    assert u_anon.is_active is False
    assert u_anon.name == "Usuário removido"
    assert "@anon.local" in u_anon.email
    assert u_anon.phone is None

    # 3. Verificar U2 (u_warn): Deve estar ativo e com notificação inserida
    res_warn = await db_session.execute(select(User).where(User.id == setup["u_warn_id"]))
    u_warn = res_warn.scalar_one()
    assert u_warn.is_active is True
    assert u_warn.name == "Inactive User 11m"
    
    # Deve possuir uma notificação de account_warning
    res_notif = await db_session.execute(
        select(Notification).where(Notification.user_id == setup["u_warn_id"], Notification.type == "account_warning")
    )
    notif = res_notif.scalar_one_or_none()
    assert notif is not None
    assert "será anonimizada em 30 dias" in notif.payload["message"]

    # Testar IDEMPOTÊNCIA da notificação de aviso (rodar de novo não deve duplicar)
    stats_again = await run_data_retention_policy(db_session)
    assert stats_again["warned_count"] == 0  # já foi avisado nos últimos 30 dias
    
    # 4. Verificar U3 (u_active): Deve permanecer intocado
    res_active = await db_session.execute(select(User).where(User.id == setup["u_active_id"]))
    u_active = res_active.scalar_one()
    assert u_active.is_active is True
    assert u_active.name == "Active User 2m"

    # 5. Verificar U4 (u_admin): Admins não são anonimizados automaticamente
    res_admin = await db_session.execute(select(User).where(User.id == setup["u_admin_id"]))
    u_admin = res_admin.scalar_one()
    assert u_admin.is_active is True
    assert u_admin.name == "Admin Inactive"

    # 6. Verificar U5 (u_prof): Profissional inativo deve ser anonimizado,
    # ter bids pendentes cancelados e documentos deletados fisicamente
    res_prof_u = await db_session.execute(select(User).where(User.id == setup["u_prof_id"]))
    u_prof = res_prof_u.scalar_one()
    assert u_prof.is_active is False
    assert u_prof.name == "Usuário removido"
    
    # Bids pendentes cancelados
    res_bid = await db_session.execute(select(Bid).where(Bid.id == setup["bid_id"]))
    bid = res_bid.scalar_one()
    assert bid.status == "cancelled"
    
    # Documentos físicos removidos
    assert not os.path.exists(setup["doc_file"])
    assert not os.path.exists(setup["doc_dir"])

    # 7. Verificar mensagens
    m1_res = await db_session.execute(
        text("SELECT content FROM messages WHERE id = :id"), {"id": setup["m1_id"]}
    )
    m1 = m1_res.fetchone()
    assert m1[0] == "[REMOVED]"

    m2_res = await db_session.execute(
        text("SELECT content FROM messages WHERE id = :id"), {"id": setup["m2_id"]}
    )
    m2 = m2_res.fetchone()
    assert m2[0] == "Mensagem recente"

    # 8. Verificar notificações
    res_n_old = await db_session.execute(select(Notification).where(Notification.id == setup["n_old_id"]))
    assert res_n_old.scalar_one_or_none() is None  # Excluída

    res_n_new = await db_session.execute(select(Notification).where(Notification.id == setup["n_new_id"]))
    assert res_n_new.scalar_one_or_none() is not None  # Mantida
