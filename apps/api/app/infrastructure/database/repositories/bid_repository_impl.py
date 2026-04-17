from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.domain.entities.bid import Bid as BidEntity
from app.domain.repositories.bid_repository import BidRepository
from app.models.bid import Bid as BidModel
from app.infrastructure.database.mappers import BidMapper

class BidRepositoryImpl(BidRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, bid_id: UUID) -> Optional[BidEntity]:
        result = await self.session.execute(select(BidModel).where(BidModel.id == bid_id))
        model = result.scalar_one_or_none()
        return BidMapper.to_entity(model) if model else None

    async def save(self, bid: BidEntity) -> BidEntity:
        # Check if exists to update or add
        result = await self.session.execute(select(BidModel).where(BidModel.id == bid.id))
        model = result.scalar_one_or_none()
        
        if model:
            # Update existing
            for key, value in bid.model_dump().items():
                setattr(model, key, value)
        else:
            # Create new
            model = BidMapper.to_model(bid)
            self.session.add(model)
        
        await self.session.flush()
        return BidMapper.to_entity(model)

    async def get_by_request_and_professional(self, request_id: UUID, professional_id: UUID) -> Optional[BidEntity]:
        result = await self.session.execute(
            select(BidModel).where(
                BidModel.request_id == request_id,
                BidModel.professional_id == professional_id
            )
        )
        model = result.scalar_one_or_none()
        return BidMapper.to_entity(model) if model else None

    async def get_pending_bids_by_request(self, request_id: UUID, exclude_bid_id: UUID) -> List[BidEntity]:
        result = await self.session.execute(
            select(BidModel).where(
                BidModel.request_id == request_id,
                BidModel.id != exclude_bid_id,
                BidModel.status == "pending"
            )
        )
        models = result.scalars().all()
        return [BidMapper.to_entity(m) for m in models]

    async def update_statuses(self, bids: List[BidEntity]) -> None:
        for bid in bids:
            await self.session.execute(
                update(BidModel)
                .where(BidModel.id == bid.id)
                .values(status=bid.status)
            )
        await self.session.flush()
