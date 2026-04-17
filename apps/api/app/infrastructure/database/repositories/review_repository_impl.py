import uuid
from typing import List, Dict, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.review import Review as ReviewEntity
from app.domain.repositories.review_repository import ReviewRepository
from app.models.review import Review as ReviewModel
from app.models.contract import Contract as ContractModel
from app.infrastructure.database.mappers import ReviewMapper

class ReviewRepositoryImpl(ReviewRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, review: ReviewEntity) -> ReviewEntity:
        model = ReviewMapper.to_model(review)
        self.db.add(model)
        await self.db.flush()
        return ReviewMapper.to_entity(model)

    async def list_by_professional(self, professional_id: uuid.UUID) -> List[ReviewEntity]:
        result = await self.db.execute(
            select(ReviewModel)
            .join(ContractModel, ReviewModel.contract_id == ContractModel.id)
            .where(
                ContractModel.professional_id == professional_id,
                ReviewModel.is_authentic == True
            )
            .order_by(ReviewModel.created_at.desc())
        )
        return [ReviewMapper.to_entity(row) for row in result.scalars().all()]

    async def get_averages(self, professional_id: uuid.UUID) -> Dict[str, float]:
        result = await self.db.execute(
            select(
                func.avg(ReviewModel.score_quality).label("avg_quality"),
                func.avg(ReviewModel.score_punctuality).label("avg_punctuality"),
                func.avg(ReviewModel.score_communication).label("avg_communication"),
                func.avg(ReviewModel.score_cleanliness).label("avg_cleanliness"),
                func.count(ReviewModel.id).label("total")
            )
            .join(ContractModel, ReviewModel.contract_id == ContractModel.id)
            .where(
                ContractModel.professional_id == professional_id,
                ReviewModel.is_authentic == True,
                ReviewModel.score_quality.isnot(None)
            )
        )
        row = result.one()
        return {
            "avg_quality": float(row.avg_quality or 0),
            "avg_punctuality": float(row.avg_punctuality or 0),
            "avg_communication": float(row.avg_communication or 0),
            "avg_cleanliness": float(row.avg_cleanliness or 0),
            "total": row.total
        }
