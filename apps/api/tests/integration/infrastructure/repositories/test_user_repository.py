import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User as UserModel, UserRole as UserModelRole
from app.domain.entities.user import User as UserEntity, UserRole as UserEntityRole
from app.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl

@pytest.mark.asyncio
async def test_user_repository_get_by_email(db_session: AsyncSession):
    # Setup
    user_id = uuid.uuid4()
    user_model = UserModel(
        id=user_id,
        name="Test User",
        email="test@example.com",
        password_hash="hashed",
        role=UserModelRole.CLIENT,
        is_active=True
    )
    db_session.add(user_model)
    await db_session.commit()
    
    repo = UserRepositoryImpl(db_session)
    
    # Execute
    entity = await repo.get_by_email("test@example.com")
    
    # Assert
    assert entity is not None
    assert entity.id == user_id
    assert entity.email == "test@example.com"
    assert entity.role == UserEntityRole.CLIENT

@pytest.mark.asyncio
async def test_user_repository_save_new(db_session: AsyncSession):
    # Setup
    repo = UserRepositoryImpl(db_session)
    new_user = UserEntity(
        id=uuid.uuid4(),
        name="New User",
        email="new@example.com",
        password_hash="hashed_new",
        role=UserEntityRole.PROFESSIONAL,
        is_active=True
    )
    
    # Execute
    saved_entity = await repo.save(new_user)
    await db_session.commit()
    
    # Verify in DB
    entity_from_db = await repo.get_by_id(new_user.id)
    assert entity_from_db is not None
    assert entity_from_db.name == "New User"
    assert entity_from_db.role == UserEntityRole.PROFESSIONAL

@pytest.mark.asyncio
async def test_user_repository_update_existing(db_session: AsyncSession):
    # Setup
    user_id = uuid.uuid4()
    user_model = UserModel(
        id=user_id,
        name="Old Name",
        email="old@example.com",
        password_hash="old_hash",
        role=UserModelRole.CLIENT,
        is_active=True
    )
    db_session.add(user_model)
    await db_session.commit()
    
    repo = UserRepositoryImpl(db_session)
    entity = await repo.get_by_id(user_id)
    entity.name = "New Name"
    
    # Execute
    await repo.save(entity)
    await db_session.commit()
    
    # Verify
    updated_entity = await repo.get_by_id(user_id)
    assert updated_entity.name == "New Name"
