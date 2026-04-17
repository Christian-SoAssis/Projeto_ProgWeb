import uuid
from typing import List
from fastapi import APIRouter, Depends, status

from app.api.v1.deps import (
    get_create_review_use_case,
    get_list_professional_reviews_use_case
)
from app.core.dependencies import get_current_user
from app.domain.entities.user import User
from app.application.use_cases.create_review_use_case import CreateReviewInput
from app.schemas.v1.reviews import ReviewCreate, ReviewResponse

router = APIRouter(tags=["Reviews"])


@router.post("/reviews", response_model=ReviewResponse,
             status_code=status.HTTP_201_CREATED)
async def create_review_endpoint(
    review_in: ReviewCreate,
    use_case = Depends(get_create_review_use_case),
    current_user: User = Depends(get_current_user),
):
    """Cliente avalia o profissional após conclusão do contrato."""
    return await use_case.execute(
        CreateReviewInput(
            client_user_id=current_user.id,
            contract_id=review_in.contract_id,
            rating=review_in.rating,
            text=review_in.text
        )
    )


@router.get("/professionals/{professional_id}/reviews",
            response_model=List[ReviewResponse])
async def list_reviews_endpoint(
    professional_id: uuid.UUID,
    use_case = Depends(get_list_professional_reviews_use_case),
):
    """Lista reviews autênticas de um profissional (endpoint público)."""
    return await use_case.execute(professional_id)
