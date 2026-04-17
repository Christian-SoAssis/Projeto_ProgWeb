import uuid
from typing import List
from app.domain.entities.review import Review
from app.domain.repositories.review_repository import ReviewRepository

class ListProfessionalReviewsUseCase:
    def __init__(self, review_repo: ReviewRepository):
        self.review_repo = review_repo

    async def execute(self, professional_id: uuid.UUID) -> List[Review]:
        return await self.review_repo.list_by_professional(professional_id)
