from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.professional import Professional as ProfessionalEntity
from app.domain.repositories.professional_repository import ProfessionalRepository
from app.models.professional import Professional as ProfessionalModel
from app.infrastructure.database.mappers import ProfessionalMapper

class ProfessionalRepositoryImpl(ProfessionalRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: UUID) -> Optional[ProfessionalEntity]:
        result = await self.session.execute(
            select(ProfessionalModel).where(ProfessionalModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        return ProfessionalMapper.to_entity(model) if model else None

    async def get_by_id(self, professional_id: UUID) -> Optional[ProfessionalEntity]:
        result = await self.session.execute(
            select(ProfessionalModel).where(ProfessionalModel.id == professional_id)
        )
        model = result.scalar_one_or_none()
        return ProfessionalMapper.to_entity(model) if model else None
