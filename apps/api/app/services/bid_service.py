"""
Bid Service — logic de negócio para bids e contratos.

Regras:
- Apenas profissional verificado pode criar bid
- Apenas pedidos com status='open' aceitam bid
- Um profissional só pode ter 1 bid por pedido (unique constraint)
- Aceitar bid: atômico — bid.status='accepted', contract criado,
  request.status='matched', outros bids='cancelled'
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.bid import Bid
from app.models.contract import Contract
from app.models.request import Request
from app.models.professional import Professional


async def create_bid(
    db: AsyncSession,
    professional_user_id: uuid.UUID,
    request_id: uuid.UUID,
    price_cents: int,
    estimated_hours: int | None = None,
    message: str | None = None,
) -> Bid:
    # 1. Buscar profissional pelo user_id
    result = await db.execute(
        select(Professional).where(Professional.user_id == professional_user_id)
    )
    professional = result.scalar_one_or_none()
    if not professional:
        raise HTTPException(status_code=404, detail="Perfil profissional não encontrado")

    # 2. Verificar se está verificado
    if not professional.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verificação de conta pendente"
        )

    # 3. Buscar o request
    result = await db.execute(select(Request).where(Request.id == request_id))
    request = result.scalar_one_or_none()
    if not request:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # 4. Verificar status do request
    if request.status != "open":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pedido não está disponível para bids"
        )

    # 5. Criar bid (unique constraint cuida do duplicado)
    bid = Bid(
        request_id=request_id,
        professional_id=professional.id,
        price_cents=price_cents,
        estimated_hours=estimated_hours,
        message=message,
        status="pending",
    )
    db.add(bid)
    try:
        await db.flush()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Você já enviou uma proposta para este pedido"
        )

    return bid


async def update_bid(
    db: AsyncSession,
    bid_id: uuid.UUID,
    client_user_id: uuid.UUID,
    new_status: str,
) -> tuple[Bid, Contract | None]:
    # 1. Buscar bid
    result = await db.execute(select(Bid).where(Bid.id == bid_id))
    bid = result.scalar_one_or_none()
    if not bid:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")

    # 2. Verificar ownership via request
    result = await db.execute(select(Request).where(Request.id == bid.request_id))
    request = result.scalar_one_or_none()
    if not request or str(request.client_id) != str(client_user_id):
        raise HTTPException(status_code=403, detail="Acesso negado")

    # 3. Verificar se já processado
    if bid.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta proposta já foi processada"
        )

    # 4. Atualizar status do bid
    bid.status = new_status
    contract = None

    # 5. Se aceito: criar contrato + atualizar request + cancelar outros bids
    if new_status == "accepted":
        contract = Contract(
            request_id=bid.request_id,
            professional_id=bid.professional_id,
            client_id=client_user_id,
            agreed_cents=bid.price_cents,
            status="active",
            started_at=datetime.now(timezone.utc),
        )
        db.add(contract)

        # Atualizar request para 'matched'
        request.status = "matched"

        # Cancelar outros bids pendentes do mesmo request
        result = await db.execute(
            select(Bid).where(
                Bid.request_id == bid.request_id,
                Bid.id != bid.id,
                Bid.status == "pending"
            )
        )
        other_bids = result.scalars().all()
        for other in other_bids:
            other.status = "cancelled"

    await db.flush()
    return bid, contract
