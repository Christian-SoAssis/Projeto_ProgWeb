import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.professional import Professional
from app.models.contract import Contract
from app.models.bid import Bid
from app.schemas.v1.professionals import ProfessionalResponse
from app.schemas.v1.panels import ProfessionalMetrics, ProfessionalUpdateRequest

router = APIRouter(prefix="/professionals", tags=["Professionals Panel"])


def _require_professional(current_user: User) -> User:
    role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if role != "professional":
        raise HTTPException(status_code=403, detail="Acesso exclusivo para profissionais")
    return current_user


@router.get("/me", response_model=ProfessionalResponse)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_professional(current_user)
    result = await db.execute(
        select(Professional).where(Professional.user_id == current_user.id)
    )
    prof = result.scalar_one_or_none()
    if not prof:
        raise HTTPException(status_code=404, detail="Perfil profissional não encontrado")
    return prof


@router.patch("/me", response_model=ProfessionalResponse)
async def update_my_profile(
    update_in: ProfessionalUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_professional(current_user)
    result = await db.execute(
        select(Professional).where(Professional.user_id == current_user.id)
    )
    prof = result.scalar_one_or_none()
    if not prof:
        raise HTTPException(status_code=404, detail="Perfil profissional não encontrado")

    if update_in.bio is not None:
        prof.bio = update_in.bio
    if update_in.service_radius_km is not None:
        prof.service_radius_km = update_in.service_radius_km
    if update_in.hourly_rate_cents is not None:
        prof.hourly_rate_cents = update_in.hourly_rate_cents

    await db.commit()
    await db.refresh(prof)
    return prof


@router.get("/me/metrics", response_model=ProfessionalMetrics)
async def get_my_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_professional(current_user)
    result = await db.execute(
        select(Professional).where(Professional.user_id == current_user.id)
    )
    prof = result.scalar_one_or_none()
    if not prof:
        raise HTTPException(status_code=404, detail="Perfil profissional não encontrado")

    # Earnings e completed_jobs
    contracts_result = await db.execute(
        select(
            func.coalesce(func.sum(Contract.agreed_cents), 0).label("earnings"),
            func.count(Contract.id).label("completed"),
        ).where(
            Contract.professional_id == prof.id,
            Contract.status == "completed",
        )
    )
    row = contracts_result.one()

    # Bids recebidos (via requests do profissional)
    bids_result = await db.execute(
        select(func.count(Bid.id)).where(
            Bid.professional_id == prof.id
        )
    )
    total_bids = bids_result.scalar() or 0

    # Pending bids
    pending_result = await db.execute(
        select(func.count(Bid.id)).where(
            Bid.professional_id == prof.id,
            Bid.status == "pending"
        )
    )
    pending_bids = pending_result.scalar() or 0

    conversion_rate = (row.completed / total_bids) if total_bids > 0 else 0.0

    return ProfessionalMetrics(
        total_earnings_cents=row.earnings,
        completed_jobs=row.completed,
        pending_bids=pending_bids,
        reputation_score=prof.reputation_score,
        conversion_rate=round(conversion_rate, 4),
    )
