import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User as UserModel, UserRole as UserModelRole
from app.models.professional import Professional as ProfessionalModel
from app.models.category import Category as CategoryModel
from app.domain.entities.professional import Professional as ProfessionalEntity, Category as CategoryEntity
from app.infrastructure.database.repositories.professional_repository_impl import ProfessionalRepositoryImpl

@pytest.fixture
async def sample_user(db_session: AsyncSession):
    user = UserModel(
        id=uuid.uuid4(),
        name="Prof User",
        email="prof@example.com",
        password_hash="hashed",
        role=UserModelRole.PROFESSIONAL,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    return user

@pytest_asyncio := pytest.mark.asyncio # Alias to avoid confusion with fixture

@pytest.mark.asyncio
async def test_professional_repository_save_and_get(db_session: AsyncSession, sample_user: UserModel):
    # Setup
    repo = ProfessionalRepositoryImpl(db_session)
    prof_id = uuid.uuid4()
    prof_entity = ProfessionalEntity(
        id=prof_id,
        user_id=sample_user.id,
        bio="Test Bio",
        hourly_rate_cents=5000,
        service_radius_km=25.0,
        document_type="ID",
        document_path="path/to/doc",
        is_verified=True,
        latitude=-23.5505,
        longitude=-46.6333,
        categories=[]
    )
    
    # Execute Save
    await repo.save(prof_entity)
    await db_session.commit()
    
    # Execute Get
    fetched = await repo.get_by_id(prof_id)
    
    # Assert
    assert fetched is not None
    assert fetched.id == prof_id
    assert fetched.user_id == sample_user.id
    assert fetched.name == "Prof User" # Should be joined from User table
    assert fetched.is_verified is True

@pytest.mark.asyncio
async def test_professional_repository_list_available_by_category(db_session: AsyncSession, sample_user: UserModel):
    # Setup
    cat1 = CategoryModel(id=uuid.uuid4(), name="Category 1", slug="cat-1", is_active=True)
    db_session.add(cat1)
    await db_session.commit()
    
    prof_id = uuid.uuid4()
    prof_model = ProfessionalModel(
        id=prof_id,
        user_id=sample_user.id,
        bio="...",
        is_verified=True,
        service_radius_km=10.0,
        hourly_rate_cents=100,
        document_type="ID"
    )
    # Add to category
    from app.models.associations import professional_categories
    db_session.add(prof_model)
    await db_session.flush() # Get prof in session
    
    # Associate via relationship or direct table insert
    # ProfessionalModel has 'categories' relationship
    prof_model.categories.append(cat1)
    await db_session.commit()
    
    repo = ProfessionalRepositoryImpl(db_session)
    
    # Execute
    results = await repo.list_available(category_id=cat1.id)
    
    # Assert
    assert len(results) == 1
    assert results[0].id == prof_id
    assert results[0].categories[0].id == cat1.id
