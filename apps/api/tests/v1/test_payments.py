import pytest
import pytest_asyncio
import uuid
import hmac
import hashlib
from datetime import datetime, timezone, timedelta, date
from unittest.mock import AsyncMock, patch
from fastapi import status
from httpx import AsyncClient
from geoalchemy2 import WKTElement
from sqlalchemy import select

from app.models.user import User, UserRole
from app.models.professional import Professional
from app.models.category import Category
from app.models.request import Request
from app.models.contract import Contract
from app.models.payment import Payment, Dispute
from app.models.commission_rate import CommissionRate
from app.models.notification import Notification
from app.core.security import create_access_token
from app.core.config import settings
from app.services.payment_service import process_payouts, check_disputes_deadline


@pytest_asyncio.fixture(scope="function")
async def setup_data(db_session):
    # 1. Users
    client_user = User(
        email=f"client_{uuid.uuid4().hex[:6]}@test.com",
        name="Payments Test Client",
        password_hash="hash",
        role=UserRole.CLIENT,
        is_active=True
    )
    prof_user = User(
        email=f"prof_{uuid.uuid4().hex[:6]}@test.com",
        name="Payments Test Professional",
        password_hash="hash",
        role=UserRole.PROFESSIONAL,
        is_active=True
    )
    admin_user = User(
        email=f"admin_{uuid.uuid4().hex[:6]}@test.com",
        name="Payments Test Admin",
        password_hash="hash",
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add_all([client_user, prof_user, admin_user])
    await db_session.flush()

    # 2. Professional
    prof = Professional(
        user_id=prof_user.id,
        bio="Profissional experiente",
        latitude=-21.55, longitude=-45.42,
        service_radius_km=20.0,
        hourly_rate_cents=8000,
        reputation_score=4.0,
        is_verified=True
    )
    db_session.add(prof)

    # 3. Category
    cat = Category(
        name="Hidráulica",
        slug=f"hid_{uuid.uuid4().hex[:4]}",
        color="#0000FF"
    )
    db_session.add(cat)
    await db_session.flush()

    # 4. Request
    req = Request(
        client_id=client_user.id,
        category_id=cat.id,
        title="Torneira vazando urgente",
        urgency="immediate",
        location=WKTElement("POINT(-45.42 -21.55)", srid=4326),
        status="matched"
    )
    db_session.add(req)
    await db_session.flush()

    # 5. Contract
    contract = Contract(
        request_id=req.id,
        professional_id=prof.id,
        client_id=client_user.id,
        agreed_cents=20000,
        status="active",
        started_at=datetime.now(timezone.utc)
    )
    db_session.add(contract)
    await db_session.flush()

    # 6. Access tokens & headers
    client_token = create_access_token(data={"sub": str(client_user.id)})
    prof_token = create_access_token(data={"sub": str(prof_user.id)})
    admin_token = create_access_token(data={"sub": str(admin_user.id)})

    return {
        "client": client_user,
        "prof_user": prof_user,
        "prof": prof,
        "admin": admin_user,
        "category": cat,
        "request": req,
        "contract": contract,
        "client_headers": {"Authorization": f"Bearer {client_token}"},
        "prof_headers": {"Authorization": f"Bearer {prof_token}"},
        "admin_headers": {"Authorization": f"Bearer {admin_token}"}
    }


@pytest.mark.asyncio
async def test_create_payment_intent_not_found(client: AsyncClient, setup_data: dict):
    """Testa erro 404 quando o contrato não existe."""
    response = await client.post(
        f"/api/v1/payments/{uuid.uuid4()}/intent",
        headers=setup_data["client_headers"]
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_open_dispute_validation(client: AsyncClient, setup_data: dict):
    """Testa validação de campos ao abrir disputa."""
    payload = {
        "payment_id": str(uuid.uuid4()),
        "reason": "Curto",  # Menor que 10 chars
        "category": "invalid"
    }
    response = await client.post(
        "/api/v1/payments/disputes",
        json=payload,
        headers=setup_data["client_headers"]
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_dynamic_commission_rate_lookup(client: AsyncClient, db_session, setup_data: dict):
    """Testa a busca de taxa de comissão dinâmica por categoria e o fallback padrão."""
    contract = setup_data["contract"]
    category = setup_data["category"]
    
    # 1. Definir taxa específica para a categoria (15%)
    cat_rate = CommissionRate(
        category_id=category.id,
        percent=15.0,
        effective_from=date.today()
    )
    # 2. Definir taxa padrão global (10%)
    default_rate = CommissionRate(
        category_id=None,
        percent=10.0,
        effective_from=date.today()
    )
    db_session.add_all([cat_rate, default_rate])
    await db_session.flush()

    # Chamar criação de intenção de pagamento
    response = await client.post(
        f"/api/v1/payments/{contract.id}/intent",
        headers=setup_data["client_headers"]
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # 15% de 20000 = 3000
    assert data["fee_cents"] == 3000
    assert data["professional_amount_cents"] == 17000

    # 3. Testar fallback para padrão quando não há taxa específica para a categoria
    # Criar outra categoria e contrato
    other_cat = Category(
        name="Pintura",
        slug=f"pin_{uuid.uuid4().hex[:4]}",
        color="#00FF00"
    )
    db_session.add(other_cat)
    await db_session.flush()

    other_req = Request(
        client_id=setup_data["client"].id,
        category_id=other_cat.id,
        title="Pintura da sala de estar",
        urgency="scheduled",
        location=WKTElement("POINT(-45.42 -21.55)", srid=4326),
        status="matched"
    )
    db_session.add(other_req)
    await db_session.flush()

    other_contract = Contract(
        request_id=other_req.id,
        professional_id=setup_data["prof"].id,
        client_id=setup_data["client"].id,
        agreed_cents=10000,
        status="active"
    )
    db_session.add(other_contract)
    await db_session.flush()

    # Chamar criação de intenção de pagamento para o outro contrato
    response2 = await client.post(
        f"/api/v1/payments/{other_contract.id}/intent",
        headers=setup_data["client_headers"]
    )
    assert response2.status_code == status.HTTP_200_OK
    data2 = response2.json()
    # 10% de 10000 = 1000 (taxa padrão)
    assert data2["fee_cents"] == 1000
    assert data2["professional_amount_cents"] == 9000


@pytest.mark.asyncio
async def test_webhook_signature_verification(client: AsyncClient, db_session):
    """Testa a validação da assinatura HMAC do webhook."""
    payload = {
        "action": "payment.created",
        "api_version": "v1",
        "data": {"id": "999"},
        "id": "111",
        "type": "payment"
    }
    
    # 1. Assinatura inválida
    response_invalid = await client.post(
        "/api/v1/payments/webhook",
        json=payload,
        headers={"x-signature": "ts=123,v1=wrong_signature", "x-request-id": "req-1"}
    )
    assert response_invalid.status_code == status.HTTP_401_UNAUTHORIZED

    # 2. Assinatura válida
    timestamp = int(datetime.now().timestamp())
    x_request_id = "req-2"
    data_to_sign = f"id:{x_request_id};ts:{timestamp};"
    secret = settings.MERCADOPAGO_WEBHOOK_SECRET or "mock-webhook-secret-123"
    h = hmac.new(secret.encode(), data_to_sign.encode(), hashlib.sha256).hexdigest()
    x_signature = f"ts={timestamp},v1={h}"

    with patch("app.services.payment_service.handle_payment_webhook", new_callable=AsyncMock) as mock_handle:
        response_valid = await client.post(
            "/api/v1/payments/webhook",
            json=payload,
            headers={"x-signature": x_signature, "x-request-id": x_request_id}
        )
        assert response_valid.status_code == status.HTTP_200_OK
        mock_handle.assert_called_once()


@pytest.mark.asyncio
async def test_webhook_payment_approved_scheduling(client: AsyncClient, db_session, setup_data: dict):
    """Testa o agendamento do repasse D+2 e notificações ao aprovar o pagamento no webhook."""
    contract = setup_data["contract"]
    
    # Criar intenção de pagamento no DB
    payment = Payment(
        contract_id=contract.id,
        amount_cents=contract.agreed_cents,
        fee_cents=2000,
        professional_amount_cents=18000,
        status="pending"
    )
    db_session.add(payment)
    await db_session.flush()

    # Mockar a resposta de detalhes do pagamento do MercadoPago
    mock_mp_payment = {
        "status": "approved",
        "external_reference": str(payment.id)
    }

    timestamp = int(datetime.now().timestamp())
    x_request_id = "req-1"
    data_to_sign = f"id:{x_request_id};ts:{timestamp};"
    secret = settings.MERCADOPAGO_WEBHOOK_SECRET or "mock-webhook-secret-123"
    h = hmac.new(secret.encode(), data_to_sign.encode(), hashlib.sha256).hexdigest()
    x_signature = f"ts={timestamp},v1={h}"

    with patch("app.services.payment_service.mercado_pago_service.get_payment_details", return_value=mock_mp_payment):
        payload = {
            "type": "payment",
            "data": {"id": "mp-pay-id-123"}
        }
        response = await client.post(
            "/api/v1/payments/webhook",
            json=payload,
            headers={"x-signature": x_signature, "x-request-id": x_request_id}
        )
        assert response.status_code == status.HTTP_200_OK

        # Atualizar objetos do banco de dados para verificação
        await db_session.refresh(payment)
        await db_session.refresh(contract)

        assert payment.status == "paid"
        assert payment.mp_payment_id == "mp-pay-id-123"
        assert contract.status == "payment_confirmed"
        assert contract.payment_confirmed_at is not None
        assert contract.payout_scheduled_at is not None
        
        # Verificar se pulou fim de semana na data do repasse (D+2 útil)
        assert contract.payout_scheduled_at > contract.payment_confirmed_at
        
        # Verificar notificação para profissional
        result = await db_session.execute(
            select(Notification).where(Notification.user_id == setup_data["prof_user"].id)
        )
        notifications = result.scalars().all()
        assert len(notifications) == 1
        assert notifications[0].type == "payment_confirmed"


@pytest.mark.asyncio
async def test_payouts_cron_job(db_session, setup_data: dict):
    """Testa se o job de payouts processa apenas contratos no prazo e sem disputas."""
    contract = setup_data["contract"]
    
    # 1. Contrato com repasse agendado para o passado (ontem)
    contract.status = "payment_confirmed"
    contract.payment_confirmed_at = datetime.now(timezone.utc) - timedelta(days=3)
    contract.payout_scheduled_at = datetime.now(timezone.utc) - timedelta(days=1)
    
    payment = Payment(
        contract_id=contract.id,
        amount_cents=contract.agreed_cents,
        fee_cents=2000,
        professional_amount_cents=18000,
        status="paid",
        mp_payment_id="mp-123"
    )
    db_session.add(payment)
    await db_session.flush()

    # 2. Contrato com repasse agendado para o futuro (amanhã)
    other_cat = Category(
        name="Serviços Gerais",
        slug=f"sg_{uuid.uuid4().hex[:4]}",
        color="#FFFFFF"
    )
    db_session.add(other_cat)
    await db_session.flush()

    other_req = Request(
        client_id=setup_data["client"].id,
        category_id=other_cat.id,
        title="Serviço geral residencial",
        urgency="scheduled",
        location=WKTElement("POINT(-45.42 -21.55)", srid=4326),
        status="matched"
    )
    db_session.add(other_req)
    await db_session.flush()

    future_contract = Contract(
        request_id=other_req.id,
        professional_id=setup_data["prof"].id,
        client_id=setup_data["client"].id,
        agreed_cents=10000,
        status="payment_confirmed",
        payment_confirmed_at=datetime.now(timezone.utc),
        payout_scheduled_at=datetime.now(timezone.utc) + timedelta(days=1)
    )
    db_session.add(future_contract)
    await db_session.flush()

    # Executar o processador de payouts
    processed_count = await process_payouts(db_session)
    assert processed_count == 1

    await db_session.refresh(contract)
    await db_session.refresh(future_contract)

    assert contract.status == "completed"
    assert contract.payout_completed_at is not None
    assert future_contract.status == "payment_confirmed"
    assert future_contract.payout_completed_at is None


@pytest.mark.asyncio
async def test_dispute_lifecycle_and_admin_resolution(client: AsyncClient, db_session, setup_data: dict):
    """Testa o ciclo de vida completo de uma disputa: abertura, resposta, escalação e resoluções do admin."""
    contract = setup_data["contract"]
    
    # Setup de pagamento confirmado para poder abrir disputa
    contract.status = "payment_confirmed"
    contract.payment_confirmed_at = datetime.now(timezone.utc) - timedelta(days=1)
    
    payment = Payment(
        contract_id=contract.id,
        amount_cents=contract.agreed_cents,
        fee_cents=2000,
        professional_amount_cents=18000,
        status="paid",
        mp_payment_id="mp-pay-111"
    )
    db_session.add(payment)
    await db_session.flush()

    # 1. ABERTURA DA DISPUTA (Cliente abre)
    dispute_payload = {
        "reason": "O profissional não realizou o serviço adequadamente.",
        "category": "quality",
        "evidence_urls": ["http://evidence1.jpg"]
    }
    response_open = await client.post(
        f"/api/v1/payments/contracts/{contract.id}/dispute",
        json=dispute_payload,
        headers=setup_data["client_headers"]
    )
    assert response_open.status_code == status.HTTP_201_CREATED
    dispute_data = response_open.json()
    dispute_id = uuid.UUID(dispute_data["id"])
    
    await db_session.refresh(contract)
    assert contract.status == "disputed"
    
    # 2. RESPOSTA DA DISPUTA (Profissional responde)
    response_payload = {
        "message": "Fiz todo o serviço conforme combinado.",
        "evidence_urls": ["http://evidence_pro.jpg"],
        "proposed_resolution": "Manter o valor total contratado."
    }
    response_reply = await client.post(
        f"/api/v1/payments/disputes/{dispute_id}/response",
        json=response_payload,
        headers=setup_data["prof_headers"]
    )
    assert response_reply.status_code == status.HTTP_200_OK
    assert response_reply.json()["status"] == "under_review"

    # 3. AUTO-ESCALAÇÃO POR PRAZO EXPIRADO
    # Criar outra disputa que vai expirar
    other_cat = Category(
        name="Elétrica",
        slug=f"el_{uuid.uuid4().hex[:4]}",
        color="#FFFF00"
    )
    db_session.add(other_cat)
    await db_session.flush()

    other_req = Request(
        client_id=setup_data["client"].id,
        category_id=other_cat.id,
        title="Problema elétrico no disjuntor",
        urgency="immediate",
        location=WKTElement("POINT(-45.42 -21.55)", srid=4326),
        status="matched"
    )
    db_session.add(other_req)
    await db_session.flush()

    other_contract = Contract(
        request_id=other_req.id,
        professional_id=setup_data["prof"].id,
        client_id=setup_data["client"].id,
        agreed_cents=10000,
        status="payment_confirmed",
        payment_confirmed_at=datetime.now(timezone.utc)
    )
    db_session.add(other_contract)
    await db_session.flush()

    other_payment = Payment(
        contract_id=other_contract.id,
        amount_cents=other_contract.agreed_cents,
        fee_cents=1000,
        professional_amount_cents=9000,
        status="paid",
        mp_payment_id="mp-pay-222"
    )
    db_session.add(other_payment)
    await db_session.flush()

    # Abrir a disputa e alterar a data limite para o passado
    expired_dispute = Dispute(
        contract_id=other_contract.id,
        opened_by_user_id=setup_data["client"].id,
        reason="Trabalho incompleto e perigoso",
        category="damage",
        status="opened",
        response_deadline=datetime.now(timezone.utc) - timedelta(hours=1),
        payment_id=other_payment.id
    )
    db_session.add(expired_dispute)
    other_contract.status = "disputed"
    await db_session.flush()

    # Chamar cron de deadlines
    escalated_count = await check_disputes_deadline(db_session)
    assert escalated_count == 1
    
    await db_session.refresh(expired_dispute)
    assert expired_dispute.status == "auto_escalated"

    # 4. ADMIN LISTA DISPUTAS
    response_list = await client.get(
        "/api/v1/admin/disputes",
        headers=setup_data["admin_headers"]
    )
    assert response_list.status_code == status.HTTP_200_OK
    disputes_list = response_list.json()
    assert len(disputes_list) >= 2

    # Filtrar por status
    response_filtered = await client.get(
        "/api/v1/admin/disputes?status=under_review",
        headers=setup_data["admin_headers"]
    )
    assert response_filtered.status_code == status.HTTP_200_OK
    assert all(d["status"] == "under_review" for d in response_filtered.json())

    # 5. ADMIN RESOLVE DISPUTA (Reembolso Total / refund_full)
    resolve_payload = {
        "resolution": "refund_full",
        "admin_notes": "Aprovado reembolso integral após análise das provas."
    }
    
    with patch("app.services.payment_service.mercado_pago_service.refund_payment", new_callable=AsyncMock) as mock_refund:
        response_resolve = await client.patch(
            f"/api/v1/admin/disputes/{dispute_id}",
            json=resolve_payload,
            headers=setup_data["admin_headers"]
        )
        assert response_resolve.status_code == status.HTTP_200_OK
        
        await db_session.refresh(contract)
        assert contract.status == "refunded"
        mock_refund.assert_called_once_with("mp-pay-111", 20000)

    # 6. ADMIN RESOLVE DISPUTA EXPIRADA (Reembolso Parcial / refund_partial)
    resolve_partial_payload = {
        "resolution": "refund_partial",
        "refund_percent": 50,
        "admin_notes": "Estorno parcial de 50% devido à falta de resposta do profissional."
    }

    with patch("app.services.payment_service.mercado_pago_service.refund_payment", new_callable=AsyncMock) as mock_refund_partial:
        response_resolve_partial = await client.patch(
            f"/api/v1/admin/disputes/{expired_dispute.id}",
            json=resolve_partial_payload,
            headers=setup_data["admin_headers"]
        )
        assert response_resolve_partial.status_code == status.HTTP_200_OK
        
        await db_session.refresh(other_contract)
        assert other_contract.status == "partially_refunded"
        mock_refund_partial.assert_called_once_with("mp-pay-222", 5000)
