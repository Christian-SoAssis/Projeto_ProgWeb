import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.review import Review as ReviewEntity
from app.infrastructure.database.repositories.review_repository_impl import ReviewRepositoryImpl
from app.models.user import User as UserModel, UserRole
from app.models.professional import Professional as ProfessionalModel
from app.models.category import Category as CategoryModel
from app.models.contract import Contract as ContractModel
from app.models.bid import Bid as BidModel
from app.models.request import Request as RequestModel

@pytest.mark.asyncio
async def test_review_repository_save_and_list(db_session: AsyncSession):
    # 1. Setup Dependencies
    user_client = UserModel(id=uuid.uuid4(), name="Client", email=f"c_{uuid.uuid4()}@ex.com", password_hash="h", role=UserRole.CLIENT)
    user_prof = UserModel(id=uuid.uuid4(), name="Prof", email=f"p_{uuid.uuid4()}@ex.com", password_hash="h", role=UserRole.PROFESSIONAL)
    db_session.add_all([user_client, user_prof])
    await db_session.flush()

    prof = ProfessionalModel(id=uuid.uuid4(), user_id=user_prof.id, bio="...", latitude=0, longitude=0)
    db_session.add(prof)
    await db_session.flush()

    cat = CategoryModel(id=uuid.uuid4(), name="Test Cat", slug="test-cat", color="#000000")
    db_session.add(cat)
    await db_session.flush()

    req = RequestModel(id=uuid.uuid4(), client_id=user_client.id, category_id=cat.id, title="Test Request", description="...", latitude=0, longitude=0, urgency="scheduled")
    db_session.add(req)
    await db_session.flush()

    bid = BidModel(id=uuid.uuid4(), request_id=req.id, professional_id=prof.id, price_cents=1000, message="...")
    db_session.add(bid)
    await db_session.flush()

    contract = ContractModel(id=uuid.uuid4(), request_id=req.id, client_id=user_client.id, professional_id=prof.id, agreed_cents=1000, status="completed")
    db_session.add(contract)
    await db_session.commit()

    repo = ReviewRepositoryImpl(db_session)
    
    # 2. Setup Review Entity
    review_entity = ReviewEntity(
        id=uuid.uuid4(),
        contract_id=contract.id,
        reviewer_id=user_client.id,
        reviewee_id=user_prof.id,
        rating=5,
        text="Excellent service!",
        is_authentic=True,
        score_quality=0.9,
        score_punctuality=1.0
    )

    # 3. Execute Save
    saved_review = await repo.save(review_entity)
    await db_session.commit()

    # 4. Verify
    assert saved_review.id == review_entity.id
    assert saved_review.text == "Excellent service!"

    # 5. Execute List
    reviews = await repo.list_by_professional(prof.id)
    assert len(reviews) == 1
    assert reviews[0].id == review_entity.id

    # 6. Execute Averages
    averages = await repo.get_averages(prof.id)
    assert averages["total"] == 1
    assert averages["avg_quality"] == 0.9
    assert averages["avg_punctuality"] == 1.0
