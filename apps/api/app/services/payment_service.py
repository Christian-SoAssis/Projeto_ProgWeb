import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.payment import Payment, Dispute
from app.models.contract import Contract
from app.models.request import Request
from app.models.category import Category
from app.services.mercado_pago_service import mercado_pago_service
from app.core.config import settings

logger = logging.getLogger(__name__)

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
    
    # 2. Verificar se já existe pagamento
    result = await db.execute(
        select(Payment).where(Payment.contract_id == contract_id)
    )
    existing_payment = result.scalar_one_or_none()
    if existing_payment and existing_payment.status == "paid":
        raise HTTPException(status_code=400, detail="Este contrato já foi pago")
    
    # 3. Buscar categoria para pegar fee_percentage
    result = await db.execute(
        select(Category)
        .join(Request, Request.category_id == Category.id)
        .where(Request.id == contract.request_id)
    )
    category = result.scalar_one_or_none()
    fee_percent = category.fee_percentage if category else 10 # Fallback 10%
    
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
        # Buscar detalhes do pagamento no MP
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
                        payment.status = "paid"
                        payment.mp_payment_id = str(resource_id)
                        
                        # Atualizar status do contrato
                        result = await db.execute(
                            select(Contract).where(Contract.id == payment.contract_id)
                        )
                        contract = result.scalar_one_or_none()
                        if contract and contract.status == "active":
                            contract.status = "payment_confirmed"
                            contract.payment_confirmed_at = datetime.now(timezone.utc)
                            logger.info(f"Contrato {contract.id} confirmado via pagamento.")
                    
                    elif status_mp in ["rejected", "cancelled", "refunded", "in_mediation"]:
                        payment.status = status_mp
                        logger.warning(f"Pagamento {payment_id} mudou para status: {status_mp}")
                    
                    await db.flush()
                else:
                    logger.error(f"Pagamento ID {payment_id} não encontrado no banco de dados.")
            except Exception as e:
                logger.error(f"Erro ao processar webhook para pagamento {external_ref}: {str(e)}")

async def create_dispute(
    db: AsyncSession, 
    user_id: uuid.UUID, 
    payment_id: uuid.UUID, 
    reason: str, 
    category: str
) -> Dispute:
    """
    Abre uma disputa para um pagamento.
    """
    # 1. Verificar se o pagamento existe e está pago
    result = await db.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    if payment.status != "paid":
        raise HTTPException(
            status_code=400, 
            detail="Só é possível abrir disputa para pagamentos confirmados"
        )

    # 2. Verificar se já existe disputa para este contrato
    result = await db.execute(
        select(Dispute).where(Dispute.contract_id == payment.contract_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=409, 
            detail="Já existe uma disputa aberta para este contrato"
        )
    
    # 3. Criar disputa
    dispute = Dispute(
        payment_id=payment_id,
        contract_id=payment.contract_id,
        opened_by_user_id=user_id,
        reason=reason,
        category=category,
        status="opened"
    )
    
    db.add(dispute)
    
    # 4. Atualizar status do contrato
    result = await db.execute(
        select(Contract).where(Contract.id == payment.contract_id)
    )
    contract = result.scalar_one_or_none()
    if contract:
        contract.status = "disputed"
        logger.info(f"Contrato {contract.id} marcado como em disputa.")
        
    await db.flush()
    return dispute
