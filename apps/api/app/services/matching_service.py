"""
Matching Service — Motor de matching v0 por regras.

Pipeline:
  1. Buscar candidatos: profissionais is_verified=True com a mesma category_id
  2. Calcular distância (haversine) entre request.location e professional.(lat, lng)
  3. Filtrar por service_radius_km do profissional (distance_km <= service_radius_km)
  4. Ordenar por reputation_score DESC
  5. Retornar top-10

Futuro (v1): substituir ordenação por LightGBM LTR quando >= 500 contratos.
"""
import math
import logging
from typing import List, Optional
from uuid import UUID
import uuid
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.professional import Professional
from app.models.request import Request
from app.models.contract import Contract
from app.models.associations import professional_categories
from app.matching.engine import matching_engine, LTR_MIN_CONTRACTS
from app.domain.services.task_queue import TaskQueue

logger = logging.getLogger(__name__)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula distância em km entre dois pontos usando fórmula haversine."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def rank_candidates(candidates: list) -> list:
    """Ordena candidatos por reputation_score DESC e retorna top-10."""
    return sorted(candidates, key=lambda x: x["reputation_score"], reverse=True)[:10]


async def get_matches_v0(
    db: AsyncSession,
    request: Request,
    category_id: UUID,
) -> List[dict]:
    """
    Matching v0 por regras:
    - Profissionais verificados na mesma categoria
    - Dentro do service_radius_km do profissional
    - Ordenados por reputation_score DESC
    - Máximo 10 resultados
    """
    # Obter lat/lng do request via hybrid_property
    req_lat = request.latitude
    req_lon = request.longitude

    if req_lat is None or req_lon is None:
        logger.warning(f"Request {request.id} sem localização válida")
        return []

    # Buscar profissionais verificados na categoria do request
    stmt = (
        select(Professional)
        .join(professional_categories,
              Professional.id == professional_categories.c.professional_id)
        .where(
            professional_categories.c.category_id == category_id,
            Professional.is_verified == True,
            Professional.latitude.isnot(None),
            Professional.longitude.isnot(None),
        )
    )
    result = await db.execute(stmt)
    professionals = result.scalars().all()

    candidates = []
    for prof in professionals:
        distance = haversine_km(req_lat, req_lon, prof.latitude, prof.longitude)
        if distance <= prof.service_radius_km:
            candidates.append({
                "id": prof.id,
                "user_id": prof.user_id,
                "bio": prof.bio,
                "latitude": prof.latitude,
                "longitude": prof.longitude,
                "service_radius_km": prof.service_radius_km,
                "hourly_rate_cents": prof.hourly_rate_cents,
                "reputation_score": prof.reputation_score,
                "is_verified": prof.is_verified,
                "distance_km": round(distance, 2),
            })

    return sorted(candidates, key=lambda x: x["reputation_score"], reverse=True)


async def get_matches_impl(
    db: AsyncSession,
    request: Request,
    task_queue: Optional[TaskQueue] = None,
) -> List[dict]:
    """
    Implementação interna do matching: recupera candidatos, aplica LTR se qualificado,
    e enfileira eventos de impressão.
    """
    candidates = await get_matches_v0(db, request, request.category_id)
    if not candidates:
        return []

    # Contar contratos concluídos no sistema
    contracts_stmt = select(func.count()).select_from(Contract).where(Contract.status == "completed")
    contracts_result = await db.execute(contracts_stmt)
    completed_contracts_count = contracts_result.scalar() or 0

    use_ltr = completed_contracts_count >= LTR_MIN_CONTRACTS and matching_engine.is_ready()

    if use_ltr:
        # Preparar as features para o LTR
        candidate_features = [
            {
                "distance_km": float(c["distance_km"]),
                "reputation_score": float(c["reputation_score"]),
                "hourly_rate_cents": float(c["hourly_rate_cents"] or 0),
                "experience_years": 0.0,
                "rating": float(c["reputation_score"]),
            }
            for c in candidates
        ]
        
        try:
            scores = matching_engine.score(candidate_features)
            for i, score in enumerate(scores):
                candidates[i]["matching_score"] = score
            candidates = sorted(candidates, key=lambda x: x["matching_score"], reverse=True)
            logger.info(f"LTR matching utilizado com sucesso para o request {request.id}")
        except Exception as e:
            logger.critical(
                f"Erro crítico no LTR matching para o request {request.id}: {e}. "
                "Fazendo fallback silencioso para V0.",
                exc_info=True
            )
            candidates = sorted(candidates, key=lambda x: x["reputation_score"], reverse=True)
    else:
        # Fallback para V0 sorting
        candidates = sorted(candidates, key=lambda x: x["reputation_score"], reverse=True)

    top_candidates = candidates[:10]

    # Enfileirar eventos de 'impression' de forma assíncrona
    if top_candidates:
        if task_queue is None:
            from app.infrastructure.services.arq_task_queue import ArqTaskQueue
            task_queue = ArqTaskQueue()
            
        impression_events = []
        for idx, cand in enumerate(top_candidates):
            feat = {
                "distance_km": float(cand["distance_km"]),
                "reputation_score": float(cand["reputation_score"]),
                "hourly_rate_cents": float(cand["hourly_rate_cents"] or 0),
                "experience_years": 0.0,
                "rating": float(cand["reputation_score"]),
            }
            if "matching_score" in cand:
                feat["matching_score"] = float(cand["matching_score"])

            evt_id = str(uuid.uuid4())
            impression_events.append({
                "id": evt_id,
                "event_type": "impression",
                "request_id": str(request.id),
                "professional_id": str(cand["id"]),
                "bid_id": None,
                "position": idx + 1,
                "features": feat,
            })
        
        try:
            await task_queue.enqueue("log_matching_event_task", impression_events)
        except Exception as queue_err:
            logger.error(f"Falha ao enfileirar eventos de impression: {queue_err}", exc_info=True)

    return top_candidates


async def get_matches(
    db: AsyncSession,
    request: Request,
    task_queue: Optional[TaskQueue] = None,
) -> List[dict]:
    """
    Entry point do matching. Usa v0 por regras ou v1 (LTR) dependendo do número de contratos completados.
    Timeout de 3s com fallback para lista vazia em caso de erro.
    """
    try:
        return await asyncio.wait_for(
            get_matches_impl(db, request, task_queue),
            timeout=3.0
        )
    except asyncio.TimeoutError:
        logger.error(f"Matching timeout para request {request.id}, retornando lista vazia")
        return []
    except Exception as e:
        logger.error(f"Erro no matching para request {request.id}: {e}", exc_info=True)
        return []
