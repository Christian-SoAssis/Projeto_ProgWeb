import uuid
import logging
from datetime import datetime, timezone, timedelta, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from fastapi import HTTPException, status

from app.models.payment import Payment, Dispute
from app.models.contract import Contract
from app.models.request import Request
from app.models.category import Category
from app.models.commission_rate import CommissionRate
from app.models.professional import Professional
from app.models.user import User, UserRole
from app.models.notification import Notification
from app.services.mercado_pago_service import mercado_pago_service
from app.core.config import settings

logger = logging.getLogger(__name__)


def calculate_d_plus_2_business_days(start_dt: datetime) -> datetime:
    """
    Calcula D+2 dias úteis a partir de uma data.
    Pula sábados (weekday = 5) e domingos (weekday = 6).
    """
    current_dt = start_dt
    added_days = 0
    while added_days < 2:
        current_dt += timedelta(days=1)
        if current_dt.weekday() < 5:  # Segunda a Sexta (0 a 4)
            added_days += 1
    return current_dt


async def create_payment_intent(db: AsyncSession, contract_id: uuid.UUID) -> Payment:
    """
    Cria uma intenção de pagamento para um contrato, gerando a preferência no MercadoPago.
    """
    # 1. Buscar contrato
    result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    
    # 2. Verificar se já existe pagamento pago
    result = await db.execute(
        select(Payment).where(Payment.contract_id == contract_id)
    )
    existing_payment = result.scalar_one_or_none()
    if existing_payment and existing_payment.status == "paid":
        raise HTTPException(status_code=400, detail="Este contrato já foi pago")
    
    # 3. Buscar categoria para pegar fee_percentage do commission_rates
    request_result = await db.execute(
        select(Request.category_id).where(Request.id == contract.request_id)
    )
    category_id = request_result.scalar_one_or_none()
    
    fee_percent = 5.0  # Fallback de 5% padrão
    today = date.today()
    
    if category_id:
        # Buscar comissão específica da categoria
        rate_result = await db.execute(
            select(CommissionRate.percent)
            .where(
                CommissionRate.category_id == category_id,
                CommissionRate.effective_from <= today,
                (CommissionRate.effective_until == None) | (CommissionRate.effective_until >= today)
            )
            .order_by(CommissionRate.effective_from.desc())
        )
        rate_percent = rate_result.scalar_one_or_none()
        if rate_percent is not None:
            fee_percent = float(rate_percent)
        else:
            # Buscar comissão padrão
            default_result = await db.execute(
                select(CommissionRate.percent)
                .where(
                    CommissionRate.category_id == None,
                    CommissionRate.effective_from <= today,
                    (CommissionRate.effective_until == None) | (CommissionRate.effective_until >= today)
                )
                .order_by(CommissionRate.effective_from.desc())
            )
            default_percent = default_result.scalar_one_or_none()
            if default_percent is not None:
                fee_percent = float(default_percent)
    
    # 4. Calcular valores
    amount_cents = contract.agreed_cents
    fee_cents = int(amount_cents * (fee_percent / 100.0))
    professional_amount_cents = amount_cents - fee_cents
    
    # 5. Criar ou atualizar Payment record
    if existing_payment:
        payment = existing_payment
        payment.fee_cents = fee_cents
        payment.professional_amount_cents = professional_amount_cents
        payment.status = "pending"
    else:
        payment = Payment(
            contract_id=contract_id,
            amount_cents=amount_cents,
            fee_cents=fee_cents,
            professional_amount_cents=professional_amount_cents,
            status="pending"
        )
        db.add(payment)
    
    await db.flush()
    
    # 6. Criar preferência no MercadoPago
    notification_url = f"{settings.GOOGLE_REDIRECT_URI.replace('/auth/google/callback', '')}/payments/webhook"
    
    mp_pref = await mercado_pago_service.create_preference(
        title=f"ServiçoJá - Contrato {contract_id}",
        amount_cents=amount_cents,
        fee_cents=fee_cents,
        external_reference=str(payment.id),
        notification_url=notification_url
    )
    
    if not mp_pref:
        raise HTTPException(status_code=500, detail="Erro ao gerar link de pagamento no provedor")
    
    payment.mp_preference_id = mp_pref.get("id")
    await db.flush()
    
    return payment


async def handle_payment_webhook(db: AsyncSession, data: dict):
    """
    Processa o webhook do MercadoPago.
    """
    topic = data.get("type") or data.get("topic")
    resource_id = data.get("data", {}).get("id") or data.get("id")
    
    if topic == "payment" or topic == "merchant_order":
        mp_payment = await mercado_pago_service.get_payment_details(resource_id)
        if not mp_payment:
            return
            
        status_mp = mp_payment.get("status")
        external_ref = mp_payment.get("external_reference")
        
        if external_ref:
            try:
                payment_id = uuid.UUID(external_ref)
                result = await db.execute(
                    select(Payment).where(Payment.id == payment_id)
                )
                payment = result.scalar_one_or_none()
                
                if payment:
                    logger.info(f"Processando webhook para pagamento {payment_id} com status {status_mp}")
                    
                    if status_mp == "approved":
                        # Evitar duplicidade de processamento se já estivesse pago
                        if payment.status == "paid":
                            return
                            
                        payment.status = "paid"
                        payment.mp_payment_id = str(resource_id)
                        
                        # Atualizar status do contrato
                        result = await db.execute(
                            select(Contract).where(Contract.id == payment.contract_id)
                        )
                        contract = result.scalar_one_or_none()
                        if contract and contract.status in ["active", "pending"]:
                            contract.status = "payment_confirmed"
                            contract.payment_confirmed_at = datetime.now(timezone.utc)
                            # Agendar repasse para D+2 úteis
                            contract.payout_scheduled_at = calculate_d_plus_2_business_days(contract.payment_confirmed_at)
                            
                            # Buscar user_id do profissional para enviar notificação
                            prof_result = await db.execute(
                                select(Professional.user_id).where(Professional.id == contract.professional_id)
                            )
                            prof_user_id = prof_result.scalar_one_or_none()
                            if prof_user_id:
                                formatted_date = contract.payout_scheduled_at.strftime("%d/%m/%Y")
                                db.add(Notification(
                                    user_id=prof_user_id,
                                    type="payment_confirmed",
                                    payload={
                                        "message": f"Pagamento confirmado — repasse previsto para {formatted_date}",
                                        "contract_id": str(contract.id)
                                    }
                                ))
                            logger.info(f"Contrato {contract.id} confirmado via pagamento. Payout agendado para {contract.payout_scheduled_at}")
                    
                    elif status_mp in ["rejected", "cancelled", "refunded", "in_mediation"]:
                        payment.status = status_mp
                        
                        # Se recusado, reverte o contrato para active e avisa o cliente
                        if status_mp in ["rejected", "cancelled"]:
                            result = await db.execute(
                                select(Contract).where(Contract.id == payment.contract_id)
                            )
                            contract = result.scalar_one_or_none()
                            if contract:
                                contract.status = "active"
                                db.add(Notification(
                                    user_id=contract.client_id,
                                    type="account_warning",
                                    payload={
                                        "message": "Pagamento não aprovado — tente novamente ou use outro método",
                                        "contract_id": str(contract.id)
                                    }
                                ))
                        logger.warning(f"Pagamento {payment_id} mudou para status: {status_mp}")
                    
                    await db.flush()
                else:
                    logger.error(f"Pagamento ID {payment_id} não encontrado no banco de dados.")
            except Exception as e:
                logger.error(f"Erro ao processar webhook para pagamento {external_ref}: {str(e)}")


async def process_payouts(db: AsyncSession) -> int:
    """
    Job/Tarefa de repasse que finaliza contratos pagos após o prazo D+2 útil.
    Retorna o número de contratos processados.
    """
    now = datetime.now(timezone.utc)
    # Selecionar contratos com status payment_confirmed prontos para payout
    result = await db.execute(
        select(Contract).where(
            Contract.status == "payment_confirmed",
            Contract.payout_scheduled_at <= now
        )
    )
    contracts = result.scalars().all()
    
    count = 0
    for contract in contracts:
        # 1. Garantir que não há disputa ativa em andamento para este contrato
        dispute_result = await db.execute(
            select(Dispute).where(
                Dispute.contract_id == contract.id,
                Dispute.status != "resolved"
            )
        )
        if dispute_result.scalar_one_or_none():
            logger.warning(f"Contrato {contract.id} tem disputa pendente. Payout retido.")
            continue
            
        # 2. Executar payout
        contract.status = "completed"
        contract.payout_completed_at = now
        
        # 3. Notificar o profissional com o valor de repasse correto
        pay_result = await db.execute(
            select(Payment.professional_amount_cents).where(Payment.contract_id == contract.id)
        )
        prof_amount_cents = pay_result.scalar_one_or_none() or contract.agreed_cents
        amount_br = f"{prof_amount_cents / 100.0:.2f}".replace('.', ',')
        
        prof_result = await db.execute(
            select(Professional.user_id).where(Professional.id == contract.professional_id)
        )
        prof_user_id = prof_result.scalar_one_or_none()
        if prof_user_id:
            db.add(Notification(
                user_id=prof_user_id,
                type="payout_completed",
                payload={
                    "message": f"Repasse de R$ {amount_br} liberado na sua conta",
                    "contract_id": str(contract.id)
                }
            ))
            
        count += 1
        logger.info(f"Payout concluído para o contrato {contract.id}.")
        
    if count > 0:
        await db.flush()
        
    return count


async def create_dispute(
    db: AsyncSession, 
    user_id: uuid.UUID, 
    contract_id: uuid.UUID, 
    reason: str, 
    category: str,
    evidence_urls: list = None
) -> Dispute:
    """
    Abre uma disputa para um contrato/pagamento.
    """
    if len(reason) < 10:
        raise HTTPException(status_code=422, detail="Motivo da disputa deve ter no mínimo 10 caracteres")
    if category not in ["quality", "no_show", "overcharge", "damage", "other"]:
        raise HTTPException(status_code=422, detail="Categoria da disputa inválida")

    # 1. Buscar contrato
    result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
        
    # Verificar permissão (deve ser cliente ou profissional do contrato)
    prof_result = await db.execute(
        select(Professional.user_id).where(Professional.id == contract.professional_id)
    )
    prof_user_id = prof_result.scalar_one_or_none()
    
    if user_id != contract.client_id and user_id != prof_user_id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para abrir disputa neste contrato")
        
    if contract.status in ["completed", "cancelled", "disputed", "refunded", "partially_refunded"]:
        raise HTTPException(
            status_code=409, 
            detail="Disputa não pode ser aberta neste status"
        )
        
    # 2. Buscar pagamento
    pay_result = await db.execute(
        select(Payment).where(Payment.contract_id == contract_id)
    )
    payment = pay_result.scalar_one_or_none()
    
    # 3. Criar disputa com prazo de 72h
    dispute = Dispute(
        contract_id=contract_id,
        payment_id=payment.id if payment else None,
        opened_by_user_id=user_id,
        reason=reason,
        category=category,
        evidence_urls=evidence_urls or [],
        status="opened",
        response_deadline=datetime.now(timezone.utc) + timedelta(hours=72)
    )
    db.add(dispute)
    
    # 4. Atualizar status do contrato para disputed
    contract.status = "disputed"
    
    # 5. Notificar a parte contrária
    opposing_user_id = prof_user_id if user_id == contract.client_id else contract.client_id
    opener_name = "O cliente" if user_id == contract.client_id else "O profissional"
    
    db.add(Notification(
        user_id=opposing_user_id,
        type="dispute_opened",
        payload={
            "message": f"{opener_name} abriu uma disputa. Você tem 72h para responder.",
            "contract_id": str(contract.id),
            "dispute_id": str(dispute.id)
        }
    ))
    
    # 6. Notificar administradores
    admin_result = await db.execute(
        select(User.id).where(User.role == "admin")
    )
    admin_ids = admin_result.scalars().all()
    for admin_id in admin_ids:
        db.add(Notification(
            user_id=admin_id,
            type="dispute_opened",
            payload={
                "message": f"Nova disputa aberta para o contrato {contract.id}.",
                "dispute_id": str(dispute.id)
            }
        ))
        
    await db.flush()
    return dispute


async def respond_to_dispute(
    db: AsyncSession,
    user_id: uuid.UUID,
    dispute_id: uuid.UUID,
    message: str,
    evidence_urls: list = None,
    proposed_resolution: str = None
) -> Dispute:
    """
    Permite à parte contrária responder à disputa dentro do prazo de 72h.
    """
    if len(message) < 10:
        raise HTTPException(status_code=422, detail="Mensagem deve ter no mínimo 10 caracteres")
    if not proposed_resolution or len(proposed_resolution) < 10:
        raise HTTPException(status_code=422, detail="Resolução proposta deve ter no mínimo 10 caracteres")

    # 1. Buscar disputa
    result = await db.execute(
        select(Dispute).where(Dispute.id == dispute_id)
    )
    dispute = result.scalar_one_or_none()
    if not dispute:
        raise HTTPException(status_code=404, detail="Disputa não encontrada")
        
    if dispute.status != "opened":
        raise HTTPException(status_code=400, detail="Disputa não aceita mais respostas")
        
    # Verificar prazo
    if datetime.now(timezone.utc) > dispute.response_deadline:
        raise HTTPException(status_code=400, detail="Prazo de resposta expirou")
        
    # Verificar se o responder é o destinatário correto (não quem abriu e sim a outra parte do contrato)
    result = await db.execute(
        select(Contract).where(Contract.id == dispute.contract_id)
    )
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato associado não encontrado")
        
    prof_result = await db.execute(
        select(Professional.user_id).where(Professional.id == contract.professional_id)
    )
    prof_user_id = prof_result.scalar_one_or_none()
    
    if user_id == dispute.opened_by_user_id:
        raise HTTPException(status_code=403, detail="Você não pode responder à disputa aberta por você mesmo")
    if user_id != contract.client_id and user_id != prof_user_id:
        raise HTTPException(status_code=403, detail="Você não faz parte deste contrato")
        
    # 2. Salvar resposta e avançar status
    dispute.response_message = message
    dispute.response_evidence_urls = evidence_urls or []
    dispute.proposed_resolution = proposed_resolution
    dispute.responded_at = datetime.now(timezone.utc)
    dispute.status = "under_review"
    
    # 3. Notificar o criador da disputa
    db.add(Notification(
        user_id=dispute.opened_by_user_id,
        type="dispute_response",
        payload={
            "message": "A outra parte respondeu à sua disputa",
            "dispute_id": str(dispute.id)
        }
    ))
    
    # 4. Notificar administradores
    admin_result = await db.execute(
        select(User.id).where(User.role == "admin")
    )
    admin_ids = admin_result.scalars().all()
    for admin_id in admin_ids:
        db.add(Notification(
            user_id=admin_id,
            type="dispute_response",
            payload={
                "message": f"Disputa #{dispute.id} pronta para arbitragem — ambas as partes se manifestaram",
                "dispute_id": str(dispute.id)
            }
        ))
        
    await db.flush()
    return dispute


async def check_disputes_deadline(db: AsyncSession) -> int:
    """
    Job diário/periódico que varre disputas pendentes e escala automaticamente após 72h.
    """
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Dispute).where(
            Dispute.status == "opened",
            Dispute.response_deadline <= now
        )
    )
    disputes = result.scalars().all()
    
    count = 0
    for dispute in disputes:
        dispute.status = "auto_escalated"
        
        # Descobrir a parte não responsiva
        result = await db.execute(
            select(Contract).where(Contract.id == dispute.contract_id)
        )
        contract = result.scalar_one_or_none()
        if contract:
            prof_result = await db.execute(
                select(Professional.user_id).where(Professional.id == contract.professional_id)
            )
            prof_user_id = prof_result.scalar_one_or_none()
            non_responsive_user_id = prof_user_id if dispute.opened_by_user_id == contract.client_id else contract.client_id
            
            db.add(Notification(
                user_id=non_responsive_user_id,
                type="dispute_response",
                payload={
                    "message": "O prazo de resposta expirou. A disputa foi encaminhada para análise.",
                    "dispute_id": str(dispute.id)
                }
            ))
            
        # Notificar admin
        admin_result = await db.execute(
            select(User.id).where(User.role == "admin")
        )
        admin_ids = admin_result.scalars().all()
        for admin_id in admin_ids:
            db.add(Notification(
                user_id=admin_id,
                type="dispute_response",
                payload={
                    "message": f"Disputa #{dispute.id} escalada automaticamente — sem resposta em 72h",
                    "dispute_id": str(dispute.id)
                }
            ))
            
        count += 1
        logger.info(f"Disputa {dispute.id} escalada automaticamente por expiração de prazo.")
        
    if count > 0:
        await db.flush()
        
    return count


async def resolve_dispute_admin(
    db: AsyncSession,
    admin_user_id: uuid.UUID,
    dispute_id: uuid.UUID,
    resolution: str,
    refund_percent: int = None,
    admin_notes: str = None
) -> Dispute:
    """
    Permite a um administrador arbitrar e encerrar uma disputa aberta.
    Executa o reembolso correspondente via MercadoPago.
    """
    # 1. Validar admin
    admin_result = await db.execute(
        select(User).where(User.id == admin_user_id)
    )
    admin = admin_result.scalar_one_or_none()
    if not admin or admin.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado — requer perfil admin")
        
    # 2. Buscar disputa
    dispute_result = await db.execute(
        select(Dispute).where(Dispute.id == dispute_id)
    )
    dispute = dispute_result.scalar_one_or_none()
    if not dispute:
        raise HTTPException(status_code=404, detail="Disputa não encontrada")
        
    if dispute.status not in ["under_review", "auto_escalated", "opened"]:
        raise HTTPException(status_code=400, detail="Disputa já está encerrada")
        
    # 3. Buscar contrato e pagamento associado
    contract_result = await db.execute(
        select(Contract).where(Contract.id == dispute.contract_id)
    )
    contract = contract_result.scalar_one_or_none()
    
    pay_result = await db.execute(
        select(Payment).where(Payment.contract_id == dispute.contract_id)
    )
    payment = pay_result.scalar_one_or_none()
    
    # 4. Executar resolução
    dispute.resolution = resolution
    dispute.admin_notes = admin_notes
    dispute.resolved_at = datetime.now(timezone.utc)
    dispute.status = "resolved"
    
    prof_result = await db.execute(
        select(Professional.user_id).where(Professional.id == contract.professional_id)
    )
    prof_user_id = prof_result.scalar_one_or_none()
    
    if resolution == "refund_full":
        # 100% de reembolso ao cliente
        refund_amount = contract.agreed_cents
        if payment and payment.mp_payment_id:
            await mercado_pago_service.refund_payment(payment.mp_payment_id, refund_amount)
            
        contract.status = "refunded"
        
        db.add(Notification(
            user_id=contract.client_id,
            type="dispute_resolved",
            payload={"message": "Disputa resolvida — reembolso total aprovado", "dispute_id": str(dispute.id)}
        ))
        if prof_user_id:
            db.add(Notification(
                user_id=prof_user_id,
                type="dispute_resolved",
                payload={"message": "Disputa resolvida — reembolso total ao cliente", "dispute_id": str(dispute.id)}
            ))
            
    elif resolution == "refund_partial":
        if not refund_percent or refund_percent < 1 or refund_percent > 99:
            raise HTTPException(status_code=422, detail="Percentual de reembolso parcial inválido (deve ser entre 1 e 99)")
            
        dispute.refund_percent = refund_percent
        refund_amount = int(contract.agreed_cents * (refund_percent / 100.0))
        if payment and payment.mp_payment_id:
            await mercado_pago_service.refund_payment(payment.mp_payment_id, refund_amount)
            
        contract.status = "partially_refunded"
        
        db.add(Notification(
            user_id=contract.client_id,
            type="dispute_resolved",
            payload={"message": f"Disputa resolvida — reembolso parcial de {refund_percent}% aprovado.", "dispute_id": str(dispute.id)}
        ))
        if prof_user_id:
            db.add(Notification(
                user_id=prof_user_id,
                type="dispute_resolved",
                payload={"message": f"Disputa resolvida — reembolso parcial de {refund_percent}% ao cliente.", "dispute_id": str(dispute.id)}
            ))
            
    elif resolution == "refund_denied":
        # Sem reembolso. O contrato volta a ficar ativo para conclusão
        contract.status = "active"
        
        db.add(Notification(
            user_id=contract.client_id,
            type="dispute_resolved",
            payload={"message": f"Disputa analisada — reembolso não concedido. Observações: {admin_notes}", "dispute_id": str(dispute.id)}
        ))
        if prof_user_id:
            db.add(Notification(
                user_id=prof_user_id,
                type="dispute_resolved",
                payload={"message": f"Disputa analisada — reembolso não concedido. Observações: {admin_notes}", "dispute_id": str(dispute.id)}
            ))
            
    await db.flush()
    return dispute
