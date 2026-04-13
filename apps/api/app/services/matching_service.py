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
from typing import List
from uuid import UUID
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.professional import Professional
from app.models.request import Request
from app.models.associations import professional_categories

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

    return rank_candidates(candidates)


async def get_matches(
    db: AsyncSession,
    request: Request,
) -> List[dict]:
    """
    Entry point do matching. Usa v0 por regras.
    Timeout de 3s com fallback para lista vazia em caso de erro.
    """
    try:
        return await asyncio.wait_for(
            get_matches_v0(db, request, request.category_id),
            timeout=3.0
        )
    except asyncio.TimeoutError:
        logger.error(f"Matching timeout para request {request.id}, retornando lista vazia")
        return []
    except Exception as e:
        logger.error(f"Erro no matching para request {request.id}: {e}")
        return []
