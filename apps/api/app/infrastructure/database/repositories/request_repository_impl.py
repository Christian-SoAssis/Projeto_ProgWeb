from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.domain.entities.request import Request as RequestEntity
from app.domain.repositories.request_repository import RequestRepository
from app.models.request import Request as RequestModel, RequestImage as RequestImageModel
from app.infrastructure.database.mappers import RequestMapper, RequestImageMapper

class RequestRepositoryImpl(RequestRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, request_id: UUID) -> Optional[RequestEntity]:
        result = await self.session.execute(
            select(RequestModel)
            .options(selectinload(RequestModel.images))
            .where(RequestModel.id == request_id)
        )
        model = result.scalar_one_or_none()
        return RequestMapper.to_entity(model) if model else None

    async def list(self, client_id: Optional[UUID] = None, limit: int = 20, offset: int = 0) -> List[RequestEntity]:
        query = select(RequestModel).options(selectinload(RequestModel.images))
        if client_id:
            query = query.where(RequestModel.client_id == client_id)
        
        query = query.order_by(RequestModel.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [RequestMapper.to_entity(m) for m in models]

    async def save(self, request: RequestEntity) -> RequestEntity:
        model = RequestMapper.to_model(request)
        self.session.add(model)
        
        # Save images
        for img in request.images:
            img_model = RequestImageMapper.to_model(img)
            self.session.add(img_model)
            
        await self.session.flush()
        return RequestMapper.to_entity(model)

    async def update(self, request: RequestEntity) -> RequestEntity:
        result = await self.session.execute(
            select(RequestModel)
            .where(RequestModel.id == request.id)
        )
        model = result.scalar_one_or_none()
        
        if model:
            # Simple updates (status, etc)
            model.status = request.status
            model.ai_complexity = request.ai_complexity
            model.ai_urgency = request.ai_urgency
            model.ai_specialties = request.ai_specialties
            model.updated_at = request.updated_at
            
        await self.session.flush()
        return RequestMapper.to_entity(model)
