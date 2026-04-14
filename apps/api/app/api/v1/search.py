from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func
from app.core.database import get_db
from app.models.professional import Professional
from app.models.associations import professional_categories
from app.schemas.v1.panels import SearchProfessionalResponse
from app.services.matching_service import haversine_km

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/professionals", response_model=List[SearchProfessionalResponse])
async def search_professionals(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(20.0, gt=0, le=200),
    q: Optional[str] = Query(None, min_length=2, max_length=100),
    category_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Busca profissionais verificados por geolocalização + texto opcional.
    Usa lat/lng do profissional (Float) e haversine para calcular distância.
    Filtra por search_vector (FTS) se q fornecido.
    """
    stmt = select(Professional).where(
        Professional.is_verified == True,
        Professional.latitude.isnot(None),
        Professional.longitude.isnot(None),
    )

    if category_id:
        stmt = stmt.join(
            professional_categories,
            Professional.id == professional_categories.c.professional_id
        ).where(professional_categories.c.category_id == category_id)

    if q:
        # FTS via search_vector (tsvector)
        stmt = stmt.where(
            Professional.search_vector.op("@@")(
                func.plainto_tsquery("portuguese", q)
            )
        )

    result = await db.execute(stmt)
    professionals = result.scalars().all()

    # Filtrar por raio e calcular distância
    candidates = []
    for prof in professionals:
        distance = haversine_km(lat, lng, prof.latitude, prof.longitude)
        if distance <= radius_km:
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

    candidates.sort(key=lambda x: (x["distance_km"], -x["reputation_score"]))
    return candidates[:limit]
