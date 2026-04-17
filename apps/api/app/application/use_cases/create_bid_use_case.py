import uuid
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional

from app.domain.entities.bid import Bid
from app.domain.repositories.bid_repository import BidRepository
from app.domain.repositories.professional_repository import ProfessionalRepository
from app.domain.repositories.request_repository import RequestRepository
from app.domain.exceptions import EntityNotFoundError, BusinessRuleViolationError

@dataclass
class CreateBidInput:
    professional_user_id: uuid.UUID
    request_id: uuid.UUID
    price_cents: int
    estimated_hours: Optional[int] = None
    message: Optional[str] = None

class CreateBidUseCase:
    def __init__(
        self,
        bid_repo: BidRepository,
        professional_repo: ProfessionalRepository,
        request_repo: RequestRepository
    ):
        self.bid_repo = bid_repo
        self.professional_repo = professional_repo
        self.request_repo = request_repo

    async def execute(self, input_data: CreateBidInput) -> Bid:
        # 1. Buscar profissional pelo user_id
        professional = await self.professional_repo.get_by_user_id(input_data.professional_user_id)
        if not professional:
            raise EntityNotFoundError("Professional", input_data.professional_user_id)

        # 2. Verificar se está verificado
        if not professional.is_verified:
            raise BusinessRuleViolationError("Verificação de conta pendente")

        # 3. Buscar o request
        request = await self.request_repo.get_by_id(input_data.request_id)
        if not request:
            raise EntityNotFoundError("Request", input_data.request_id)

        # 4. Verificar status do request
        if not request.can_accept_bids():
            raise BusinessRuleViolationError("Pedido não está disponível para bids")

        # 5. Verificar se já existe bid (opcional, o repo pode lidar ou podemos checar aqui)
        existing_bid = await self.bid_repo.get_by_request_and_professional(
            input_data.request_id, professional.id
        )
        if existing_bid:
            raise BusinessRuleViolationError("Você já enviou uma proposta para este pedido")

        # 6. Criar bid
        bid = Bid(
            id=uuid.uuid4(),
            request_id=input_data.request_id,
            professional_id=professional.id,
            price_cents=input_data.price_cents,
            estimated_hours=input_data.estimated_hours,
            message=input_data.message,
            status="pending",
            created_at=datetime.now(timezone.utc)
        )

        return await self.bid_repo.save(bid)
