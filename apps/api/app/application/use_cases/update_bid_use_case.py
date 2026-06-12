import uuid
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional, Tuple

from app.domain.entities.bid import Bid
from app.domain.entities.contract import Contract
from app.domain.repositories.bid_repository import BidRepository
from app.domain.repositories.contract_repository import ContractRepository
from app.domain.repositories.request_repository import RequestRepository
from app.domain.exceptions import EntityNotFoundError, BusinessRuleViolationError, UnauthorizedError

@dataclass
class UpdateBidInput:
    bid_id: uuid.UUID
    client_user_id: uuid.UUID
    new_status: str
    scheduled_start: Optional[datetime] = None

from app.domain.services.task_queue import TaskQueue

class UpdateBidUseCase:
    def __init__(
        self,
        bid_repo: BidRepository,
        contract_repo: ContractRepository,
        request_repo: RequestRepository,
        task_queue: Optional[TaskQueue] = None
    ):
        self.bid_repo = bid_repo
        self.contract_repo = contract_repo
        self.request_repo = request_repo
        if task_queue is None:
            from app.infrastructure.services.arq_task_queue import ArqTaskQueue
            self.task_queue = ArqTaskQueue()
        else:
            self.task_queue = task_queue

    async def execute(self, input_data: UpdateBidInput) -> Tuple[Bid, Optional[Contract]]:
        # 1. Buscar bid
        bid = await self.bid_repo.get_by_id(input_data.bid_id)
        if not bid:
            raise EntityNotFoundError("Bid", input_data.bid_id)

        # 2. Verificar ownership via request
        request = await self.request_repo.get_by_id(bid.request_id)
        if not request:
             raise EntityNotFoundError("Request", bid.request_id)
        
        if request.client_id != input_data.client_user_id:
            raise UnauthorizedError("Acesso negado")

        # 3. Verificar se já processado
        if not bid.is_pending():
            raise BusinessRuleViolationError("Esta proposta já foi processada")

        # 4. Atualizar status do bid
        bid.status = input_data.new_status
        contract = None

        # 5. Se aceito: criar contrato + atualizar request + cancelar outros bids
        if input_data.new_status == "accepted":
            scheduled_start = input_data.scheduled_start
            scheduled_end = None
            if scheduled_start and bid.estimated_hours:
                from datetime import timedelta
                scheduled_end = scheduled_start + timedelta(hours=bid.estimated_hours)
            elif scheduled_start:
                from datetime import timedelta
                scheduled_end = scheduled_start + timedelta(hours=1)

            contract = Contract(
                id=uuid.uuid4(),
                request_id=bid.request_id,
                professional_id=bid.professional_id,
                client_id=input_data.client_user_id,
                agreed_cents=bid.price_cents,
                status="active",
                created_at=datetime.now(timezone.utc),
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end
            )
            await self.contract_repo.save(contract)

            # Atualizar request para 'matched'
            request.status = "matched"
            await self.request_repo.update(request)

            # Cancelar outros bids pendentes do mesmo request
            other_bids = await self.bid_repo.get_pending_bids_by_request(
                bid.request_id, exclude_bid_id=bid.id
            )
            for other in other_bids:
                other.status = "cancelled"
            
            await self.bid_repo.update_statuses(other_bids)

            # Registrar evento de conversão no motor de matching
            try:
                conversion_evt = {
                    "id": str(uuid.uuid4()),
                    "event_type": "conversion",
                    "request_id": str(bid.request_id),
                    "professional_id": str(bid.professional_id),
                    "bid_id": str(bid.id),
                    "position": None,
                    "features": None,
                }
                await self.task_queue.enqueue("log_matching_event_task", [conversion_evt])
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(
                    f"Falha ao enfileirar evento de conversao para bid {bid.id}: {e}",
                    exc_info=True
                )

        # Salvar o bid atualizado
        updated_bid = await self.bid_repo.save(bid)
        
        return updated_bid, contract
