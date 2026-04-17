from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List
from app.domain.entities.bid import Bid

class BidRepository(ABC):
    @abstractmethod
    async def get_by_id(self, bid_id: UUID) -> Optional[Bid]:
        pass

    @abstractmethod
    async def save(self, bid: Bid) -> Bid:
        pass

    @abstractmethod
    async def get_by_request_and_professional(self, request_id: UUID, professional_id: UUID) -> Optional[Bid]:
        pass

    @abstractmethod
    async def get_pending_bids_by_request(self, request_id: UUID, exclude_bid_id: UUID) -> List[Bid]:
        pass

    @abstractmethod
    async def update_statuses(self, bids: List[Bid]) -> None:
        pass
