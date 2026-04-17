import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.category import Category
from app.infrastructure.database.repositories.category_repository_impl import CategoryRepositoryImpl
from app.domain.entities.professional import Category as DomainCategory

@pytest.mark.asyncio
async def test_list_active_categories(db_session: AsyncSession):
    # Setup
    cat1 = Category(id=uuid.uuid4(), name="Active 1", slug="active-1", is_active=True, sort_order=1)
    cat2 = Category(id=uuid.uuid4(), name="Active 2", slug="active-2", is_active=True, sort_order=0)
    cat3 = Category(id=uuid.uuid4(), name="Inactive", slug="inactive", is_active=False)
    
    db_session.add_all([cat1, cat2, cat3])
    await db_session.commit()
    
    repo = CategoryRepositoryImpl(db_session)
    
    # Execute
    active_categories = await repo.list_active()
    
    # Assert
    assert len(active_categories) == 2
    # Order should be Active 2 (sort_order 0) then Active 1 (sort_order 1)
    assert active_categories[0].name == "Active 2"
    assert active_categories[1].name == "Active 1"
    assert isinstance(active_categories[0], DomainCategory)
