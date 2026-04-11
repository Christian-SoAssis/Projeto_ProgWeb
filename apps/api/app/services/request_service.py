import os
import uuid
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.request import Request, RequestImage
from app.schemas.v1.requests import RequestCreate
from app.core.config import settings
from arq import create_pool
from arq.connections import RedisSettings
import aiofiles
import logging

logger = logging.getLogger(__name__)

class RequestService:
    async def create_request(
        self, 
        db: AsyncSession, 
        client_id: uuid.UUID, 
        data: RequestCreate, 
        images: List[UploadFile]
    ) -> Request:
        # 1. Criar o pedido (Request)
        # Convertemos latitude/longitude para ponto WKT para o GeoAlchemy2
        point = f"POINT({data.longitude} {data.latitude})"
        
        new_request = Request(
            client_id=client_id,
            category_id=data.category_id,
            title=data.title,
            description=data.description,
            urgency=data.urgency,
            budget_cents=data.budget_cents,
            location=point,
            status="open"
        )
        
        db.add(new_request)
        await db.flush() # Para pegar o ID do request
        
        # 2. Processar Imagens
        if images:
            os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
            
            for img in images:
                file_ext = img.filename.split(".")[-1]
                file_name = f"{uuid.uuid4()}.{file_ext}"
                file_path = os.path.join(settings.UPLOADS_DIR, file_name)
                
                # Salvar no disco assincronamente
                async with aiofiles.open(file_path, "wb") as f:
                    content = await img.read()
                    await f.write(content)
                    
                new_image = RequestImage(
                    request_id=new_request.id,
                    url=file_path,
                    content_type=img.content_type,
                    size_bytes=len(content)
                )
                db.add(new_image)

        await db.commit()
        await db.refresh(new_request)
        
        # 3. Disparar Job de Análise IA (ARQ)
        try:
            redis = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
            await redis.enqueue_job("analyze_request_task", str(new_request.id))
            logger.info(f"Job de análise IA enfileirado para o pedido {new_request.id}")
        except Exception as e:
            logger.error(f"Falha ao enfileirar job ARQ: {str(e)}")
            
        return new_request

    async def get_request(self, db: AsyncSession, request_id: uuid.UUID) -> Optional[Request]:
        query = select(Request).where(Request.id == request_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def list_requests(
        self, 
        db: AsyncSession, 
        client_id: Optional[uuid.UUID] = None, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Request]:
        query = select(Request)
        if client_id:
            query = query.where(Request.client_id == client_id)
        
        query = query.order_by(Request.created_at.desc()).limit(limit).offset(offset)
        result = await db.execute(query)
        return result.scalars().all()

request_service = RequestService()
