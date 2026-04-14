import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.v1.reviews import ReviewCreate, ReviewResponse
from app.services.review_service import create_review, list_reviews_for_professional

router = APIRouter(tags=["Reviews"])


@router.post("/reviews", response_model=ReviewResponse,
             status_code=status.HTTP_201_CREATED)
async def create_review_endpoint(
    review_in: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cliente avalia o profissional após conclusão do contrato."""
    review = await create_review(
        db=db,
        client_user_id=current_user.id,
        contract_id=review_in.contract_id,
        rating=review_in.rating,
        text=review_in.text,
    )
    await db.commit()
    await db.refresh(review)
    return review


@router.get("/professionals/{professional_id}/reviews",
            response_model=List[ReviewResponse])
async def list_reviews_endpoint(
    professional_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Lista reviews autênticas de um profissional (endpoint público)."""
    return await list_reviews_for_professional(db, professional_id)
