import asyncio
from typing import Any, Dict
from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import settings
from app.core.database import async_session_maker
from app.models.request import Request, RequestImage
from app.models.category import Category
from app.services.vlm_service import vlm_service
from sqlalchemy import select, update
import aiofiles
import os
import logging

logger = logging.getLogger(__name__)

async def analyze_request_task(ctx: Dict[str, Any], request_id: str) -> str:
    """
    Job assíncrono para analisar as imagens de um pedido e atualizar os dados via IA.
    """
    logger.info(f"Iniciando análise IA para o pedido: {request_id}")
    
    async with async_session_maker() as session:
        # 1. Buscar o pedido e suas imagens
        query = select(Request).where(Request.id == request_id)
        result = await session.execute(query)
        request = result.scalar_one_or_none()
        
        if not request:
            return f"Erro: Pedido {request_id} não encontrado."
            
        images_query = select(RequestImage).where(RequestImage.request_id == request_id)
        images_result = await session.execute(images_query)
        images = images_result.scalars().all()
        
        if not images:
            return f"Aviso: Pedido {request_id} não possui imagens para análise."

        # 2. Ler os bytes das imagens do disco
        image_contents = []
        for img in images:
            if os.path.exists(img.url):
                async with aiofiles.open(img.url, mode='rb') as f:
                    image_contents.append(await f.read())
        
        if not image_contents:
            return "Erro: Não foi possível ler nenhuma imagem do disco."

        # 3. Chamar a IA (Gemini Vision)
        ai_data = await vlm_service.analyze_images(image_contents)
        
        # 4. Encontrar o category_id baseado no nome sugerido pela IA (se necessário converter de volta)
        # Por simplicidade, se a IA sugeriu um nome da lista, tentamos bater com o DB
        category_id = request.category_id
        if ai_data.get("category"):
            cat_query = select(Category.id).where(Category.name == ai_data["category"])
            cat_result = await session.execute(cat_query)
            new_cat_id = cat_result.scalar_one_or_none()
            if new_cat_id:
                category_id = new_cat_id

        # 5. Atualizar o pedido
        await session.execute(
            update(Request).where(Request.id == request_id).values(
                ai_complexity=ai_data.get("ai_complexity"),
                ai_urgency=ai_data.get("ai_urgency"),
                ai_specialties=ai_data.get("ai_specialties"),
                category_id=category_id
            )
        )
        
        # Marcar imagens como analisadas
        await session.execute(
            update(RequestImage).where(RequestImage.request_id == request_id).values(analyzed=True)
        )
        
        await session.commit()
        
    return f"Sucesso: Pedido {request_id} analisado pela IA."

# Configuração da classe de Worker do ARQ
class WorkerSettings:
    functions = [analyze_request_task]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    
    # Contexto compartilhado entre jobs
    async def on_startup(ctx):
        logger.info("Worker iniciado. Aguardando jobs...")
        
    async def on_shutdown(ctx):
        logger.info("Worker finalizando...")
