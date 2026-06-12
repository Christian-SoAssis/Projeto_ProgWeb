import asyncio
from typing import Any, Dict
from arq import create_pool, cron
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


async def process_payouts_task(ctx: Dict[str, Any]) -> str:
    """
    Job assíncrono para processar pagamentos agendados e liberados (D+2).
    """
    logger.info("Iniciando processamento de repasses (payouts)...")
    from app.services.payment_service import process_payouts
    async with async_session_maker() as session:
        count = await process_payouts(session)
        await session.commit()
    return f"Sucesso: {count} repasses processados."


async def check_disputes_deadline_task(ctx: Dict[str, Any]) -> str:
    """
    Job assíncrono para checar prazos de resposta de disputas e auto-escalar se necessário.
    """
    logger.info("Iniciando verificação de prazos de disputas...")
    from app.services.payment_service import check_disputes_deadline
    async with async_session_maker() as session:
        count = await check_disputes_deadline(session)
        await session.commit()
    return f"Sucesso: {count} disputas escaladas por expiração de prazo."


async def run_data_retention_policy_task(ctx: Dict[str, Any]) -> str:
    """
    Job assíncrono diário para rodar a política de retenção de dados da LGPD.
    """
    logger.info("Iniciando execução da política de retenção de dados da LGPD...")
    from app.services.lgpd_service import run_data_retention_policy
    async with async_session_maker() as session:
        stats = await run_data_retention_policy(session)
        await session.commit()
    return f"Sucesso: {stats['anon_count']} contas anonimizadas, {stats['warned_count']} avisadas, {stats['messages_purged_count']} mensagens limpas, {stats['notifications_purged_count']} notificações removidas."


async def log_matching_event_task(ctx: Dict[str, Any], events: list) -> str:
    """
    Job assíncrono para persistir eventos de matching no banco de dados.
    """
    logger.info(f"Persistindo {len(events)} eventos de matching...")
    from app.models.matching_event import MatchingEvent
    import uuid

    async with async_session_maker() as session:
        for evt_data in events:
            bid_id = evt_data.get("bid_id")
            if bid_id is not None:
                bid_id = uuid.UUID(bid_id) if isinstance(bid_id, str) else bid_id
            
            evt = MatchingEvent(
                id=uuid.UUID(evt_data["id"]) if isinstance(evt_data.get("id"), str) else (evt_data.get("id") or uuid.uuid4()),
                event_type=evt_data["event_type"],
                request_id=uuid.UUID(evt_data["request_id"]) if isinstance(evt_data["request_id"], str) else evt_data["request_id"],
                professional_id=uuid.UUID(evt_data["professional_id"]) if isinstance(evt_data["professional_id"], str) else evt_data["professional_id"],
                bid_id=bid_id,
                position=evt_data.get("position"),
                features=evt_data.get("features"),
            )
            session.add(evt)
        await session.commit()
    return f"Sucesso: {len(events)} eventos persistidos."


# Configuração da classe de Worker do ARQ
class WorkerSettings:
    functions = [
        analyze_request_task,
        process_payouts_task,
        check_disputes_deadline_task,
        run_data_retention_policy_task,
        log_matching_event_task
    ]
    cron_jobs = [
        cron(run_data_retention_policy_task, hour=3, minute=0)  # Executa diariamente às 3h
    ]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    
    # Contexto compartilhado entre jobs
    async def on_startup(ctx):
        logger.info("Worker iniciado. Aguardando jobs...")
        
    async def on_shutdown(ctx):
        logger.info("Worker finalizando...")

