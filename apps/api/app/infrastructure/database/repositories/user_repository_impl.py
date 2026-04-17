from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.mappers import UserMapper
from app.models.user import User as UserModel

class UserRepositoryImpl(UserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        query = select(UserModel).where(UserModel.id == user_id)
        result = await self.db.execute(query)
        model = result.scalar_one_or_none()
        return UserMapper.to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(UserModel).where(UserModel.email == email)
        result = await self.db.execute(query)
        model = result.scalar_one_or_none()
        return UserMapper.to_entity(model) if model else None

    async def save(self, user: User) -> User:
        # Check if exists
        query = select(UserModel).where(UserModel.id == user.id)
        result = await self.db.execute(query)
        model = result.scalar_one_or_none()

        if model:
            # Update
            model.name = user.name
            model.email = user.email
            model.phone = user.phone
            model.password_hash = user.password_hash
            model.role = user.role
            model.is_active = user.is_active
        else:
            model = UserMapper.to_model(user)
            self.db.add(model)
        
        await self.db.flush()
        return UserMapper.to_entity(model)
