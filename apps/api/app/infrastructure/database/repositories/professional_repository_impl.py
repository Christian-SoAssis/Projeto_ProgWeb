from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models.professional import Professional as ProfessionalModel
from app.domain.entities.professional import Professional
from app.domain.repositories.professional_repository import ProfessionalRepository
from app.infrastructure.database.mappers import ProfessionalMapper

class ProfessionalRepositoryImpl(ProfessionalRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, professional_id: UUID) -> Optional[Professional]:
        query = (
            select(ProfessionalModel)
            .options(
                joinedload(ProfessionalModel.user),
                joinedload(ProfessionalModel.categories)
            )
            .where(ProfessionalModel.id == professional_id)
        )
        result = await self.db.execute(query)
        model = result.scalar_one_or_none()
        return ProfessionalMapper.to_entity(model) if model else None

    async def list_available(self, category_id: Optional[UUID] = None) -> List[Professional]:
        query = select(ProfessionalModel).options(joinedload(ProfessionalModel.user))
        if category_id:
            query = query.filter(ProfessionalModel.categories.any(id=category_id))
        
        result = await self.db.execute(query)
        models = result.scalars().all()
        return [ProfessionalMapper.to_entity(m) for m in models]

    async def save(self, professional: Professional) -> Professional:
        # Check if exists for update
        existing = await self.db.get(ProfessionalModel, professional.id)
        if existing:
            # Manual update of fields
            existing.bio = professional.bio
            existing.hourly_rate_cents = professional.hourly_rate_cents
            existing.service_radius_km = professional.service_radius_km
            existing.document_path = professional.document_path
            existing.is_verified = professional.is_verified
            model = existing
        else:
            model = ProfessionalMapper.to_model(professional)
            self.db.add(model)
        
        await self.db.flush()
        return ProfessionalMapper.to_entity(model)
