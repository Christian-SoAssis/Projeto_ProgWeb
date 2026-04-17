import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.favorite import Favorite as FavoriteEntity
from app.infrastructure.database.repositories.favorite_repository_impl import FavoriteRepositoryImpl
from app.models.user import User as UserModel, UserRole
from app.models.professional import Professional as ProfessionalModel

@pytest.mark.asyncio
async def test_favorite_repository_lifecycle(db_session: AsyncSession):
    # 1. Setup
    client_id = uuid.uuid4()
    prof_user_id = uuid.uuid4()
    prof_id = uuid.uuid4()
    
    user_client = UserModel(id=client_id, name="Client", email=f"c_{uuid.uuid4()}@ex.com", password_hash="h", role=UserRole.CLIENT)
    user_prof = UserModel(id=prof_user_id, name="Prof", email=f"p_{uuid.uuid4()}@ex.com", password_hash="h", role=UserRole.PROFESSIONAL)
    db_session.add_all([user_client, user_prof])
    await db_session.flush()
    
    prof = ProfessionalModel(id=prof_id, user_id=prof_user_id, bio="...", latitude=0, longitude=0)
    db_session.add(prof)
    await db_session.commit()
    
    repo = FavoriteRepositoryImpl(db_session)
    
    # 2. Test Exists (False)
    assert await repo.exists(client_id, prof_id) is False
    
    # 3. Test Save
    fav_entity = FavoriteEntity(id=uuid.uuid4(), client_id=client_id, professional_id=prof_id)
    saved = await repo.save(fav_entity)
    await db_session.commit()
    
    assert saved.id == fav_entity.id
    
    # 4. Test Exists (True)
    assert await repo.exists(client_id, prof_id) is True
    
    # 5. Test List
    favorites = await repo.list_by_client(client_id)
    assert len(favorites) == 1
    assert favorites[0].professional_id == prof_id
    
    # 6. Test Delete
    await repo.delete(client_id, prof_id)
    await db_session.commit()
    
    assert await repo.exists(client_id, prof_id) is False
