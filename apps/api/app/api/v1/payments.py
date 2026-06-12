import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.payment import Payment
from app.schemas.v1.payments import (
    PaymentResponse,
    WebhookPayload,
    DisputeCreate,
    DisputeResponse,
    ContractDisputeCreate,
    DisputeResponseCreate
)
from app.services import payment_service
from app.services.mercado_pago_service import mercado_pago_service

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/{contract_id}/intent", response_model=PaymentResponse)
async def create_payment_intent(
    contract_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Gera uma intenção de pagamento para um contrato ativo.
    """
    try:
        payment = await payment_service.create_payment_intent(db, contract_id)
        await db.commit()
        return payment
    except HTTPException as e:
        raise e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def payment_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Recebe notificações do MercadoPago (Split, Pagamento, Estorno).
    """
    x_signature = request.headers.get("x-signature")
    x_request_id = request.headers.get("x-request-id")
    body = await request.body()
    
    if not mercado_pago_service.verify_webhook_signature(x_signature, x_request_id, body.decode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Assinatura inválida")
    
    try:
        payload = await request.json()
        await payment_service.handle_payment_webhook(db, payload)
        await db.commit()
        return {"status": "ok"}
    except Exception as e:
        await db.rollback()
        return {"status": "error", "detail": str(e)}

@router.post("/disputes", response_model=DisputeResponse, status_code=status.HTTP_201_CREATED)
async def open_dispute(
    dispute_in: DisputeCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Abre uma disputa para um pagamento realizado (legado/suporte a payment_id).
    """
    try:
        # Buscar contract_id correspondente
        result = await db.execute(
            select(Payment).where(Payment.id == dispute_in.payment_id)
        )
        payment = result.scalar_one_or_none()
        if not payment:
            raise HTTPException(status_code=404, detail="Pagamento não encontrado")
            
        dispute = await payment_service.create_dispute(
            db, 
            user.id, 
            payment.contract_id, 
            dispute_in.reason, 
            dispute_in.category
        )
        await db.commit()
        return dispute
    except HTTPException as e:
        raise e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contracts/{contract_id}/dispute", response_model=DisputeResponse, status_code=status.HTTP_201_CREATED)
async def open_contract_dispute(
    contract_id: uuid.UUID,
    dispute_in: ContractDisputeCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Abre uma disputa para um contrato específico.
    """
    try:
        dispute = await payment_service.create_dispute(
            db,
            user.id,
            contract_id,
            dispute_in.reason,
            dispute_in.category,
            dispute_in.evidence_urls
        )
        await db.commit()
        return dispute
    except HTTPException as e:
        raise e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/disputes/{dispute_id}/response", response_model=DisputeResponse)
async def respond_to_dispute(
    dispute_id: uuid.UUID,
    response_in: DisputeResponseCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Responde a uma disputa aberta.
    """
    try:
        dispute = await payment_service.respond_to_dispute(
            db,
            user.id,
            dispute_id,
            response_in.message,
            response_in.evidence_urls,
            response_in.proposed_resolution
        )
        await db.commit()
        return dispute
    except HTTPException as e:
        raise e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
