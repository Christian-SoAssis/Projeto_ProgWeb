import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.schemas.v1.bids import (
    BidCreate, BidUpdate, BidResponse,
    BidAcceptResponse, BidRejectResponse, ContractResponse
)
from app.services.bid_service import create_bid, update_bid

router = APIRouter(prefix="/bids", tags=["Bids"])


@router.post("", response_model=BidResponse, status_code=status.HTTP_201_CREATED)
async def create_bid_endpoint(
    bid_in: BidCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Profissional verificado envia proposta para um pedido aberto."""
    role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if role != "professional":
        raise HTTPException(status_code=403, detail="Apenas profissionais podem enviar propostas")

    bid = await create_bid(
        db=db,
        professional_user_id=current_user.id,
        request_id=bid_in.request_id,
        price_cents=bid_in.price_cents,
        estimated_hours=bid_in.estimated_hours,
        message=bid_in.message,
    )
    await db.commit()
    await db.refresh(bid)
    return bid


@router.patch("/{bid_id}")
async def update_bid_endpoint(
    bid_id: uuid.UUID,
    bid_in: BidUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cliente aceita ou rejeita um bid. Ao aceitar, cria contrato automaticamente."""
    role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if role != "client":
        raise HTTPException(status_code=403, detail="Apenas clientes podem aceitar ou rejeitar propostas")

    bid, contract = await update_bid(
        db=db,
        bid_id=bid_id,
        client_user_id=current_user.id,
        new_status=bid_in.status,
    )
    await db.commit()
    await db.refresh(bid)

    bid_data = BidResponse.model_validate(bid)

    if contract:
        await db.refresh(contract)
        contract_data = ContractResponse.model_validate(contract)
        return BidAcceptResponse(bid=bid_data, contract=contract_data)

    return BidRejectResponse(bid=bid_data)
