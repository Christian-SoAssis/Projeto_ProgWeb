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
from app.api.v1.deps import get_create_bid_use_case, get_update_bid_use_case
from app.application.use_cases.create_bid_use_case import CreateBidUseCase, CreateBidInput
from app.application.use_cases.update_bid_use_case import UpdateBidUseCase, UpdateBidInput
from app.domain.exceptions import DomainError, EntityNotFoundError, BusinessRuleViolationError, UnauthorizedError

router = APIRouter(prefix="/bids", tags=["Bids"])


@router.post("", response_model=BidResponse, status_code=status.HTTP_201_CREATED)
async def create_bid_endpoint(
    bid_in: BidCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    use_case: CreateBidUseCase = Depends(get_create_bid_use_case),
):
    """Profissional verificado envia proposta para um pedido aberto."""
    role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if role != "professional":
        raise HTTPException(status_code=403, detail="Apenas profissionais podem enviar propostas")

    try:
        bid = await use_case.execute(CreateBidInput(
            professional_user_id=current_user.id,
            request_id=bid_in.request_id,
            price_cents=bid_in.price_cents,
            estimated_hours=bid_in.estimated_hours,
            message=bid_in.message,
        ))
        await db.commit()
        return bid
    except (EntityNotFoundError, BusinessRuleViolationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{bid_id}")
async def update_bid_endpoint(
    bid_id: uuid.UUID,
    bid_in: BidUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    use_case: UpdateBidUseCase = Depends(get_update_bid_use_case),
):
    """Cliente aceita ou rejeita um bid. Ao aceitar, cria contrato automaticamente."""
    role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if role != "client":
        raise HTTPException(status_code=403, detail="Apenas clientes podem aceitar ou rejeitar propostas")

    try:
        bid, contract = await use_case.execute(UpdateBidInput(
            bid_id=bid_id,
            client_user_id=current_user.id,
            new_status=bid_in.status,
        ))
        await db.commit()

        bid_data = BidResponse.model_validate(bid)

        if contract:
            contract_data = ContractResponse.model_validate(contract)
            return BidAcceptResponse(bid=bid_data, contract=contract_data)

        return BidRejectResponse(bid=bid_data)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except (BusinessRuleViolationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
