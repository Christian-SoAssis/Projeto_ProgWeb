from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.contract import Contract as ContractEntity
from app.domain.repositories.contract_repository import ContractRepository
from app.models.contract import Contract as ContractModel
from app.infrastructure.database.mappers import ContractMapper

class ContractRepositoryImpl(ContractRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, contract: ContractEntity) -> ContractEntity:
        model = ContractMapper.to_model(contract)
        self.session.add(model)
        await self.session.flush()
        # Note: Contract model doesn't have a simple to_entity in mapper yet, but we can add it if needed.
        # For now, return the entity itself as we just saved it.
        return contract

    async def count_completed_by_professional(self, professional_id: UUID) -> int:
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count(ContractModel.id))
            .where(
                ContractModel.professional_id == professional_id,
                ContractModel.status == "completed"
            )
        )
        return result.scalar() or 0

    async def get_by_id(self, contract_id: UUID) -> Optional[ContractEntity]:
        result = await self.session.execute(select(ContractModel).where(ContractModel.id == contract_id))
        model = result.scalar_one_or_none()
        return ContractMapper.to_entity(model) if model else None
