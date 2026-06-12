from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import User, UserRole
from app.models.professional import Professional
from app.models.payment import Dispute
from app.schemas.v1.auth import ProfessionalResponse
from app.schemas.v1.payments import DisputeResponse, DisputeResolve

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.patch("/professionals/{prof_id}", response_model=ProfessionalResponse)
async def verify_professional(
    prof_id: UUID,
    status_update: str, # "verified" | "rejected"
    reason: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin aprova ou rejeita um profissional."""
    result = await db.execute(select(Professional).where(Professional.id == prof_id))
    professional = result.scalar_one_or_none()
    
    if not professional:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
    
    if status_update == "verified":
        professional.is_verified = True
        professional.rejection_reason = None
    elif status_update == "rejected":
        professional.is_verified = False
        professional.rejection_reason = reason
    else:
        raise HTTPException(status_code=400, detail="Status inválido")
        
    await db.commit()
    await db.refresh(professional)
    return professional

@router.get("/professionals", response_model=List[ProfessionalResponse])
async def list_pending_professionals(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Lista profissionais pendentes de verificação."""
    result = await db.execute(
        select(Professional)
        .where(Professional.is_verified == False)
        .order_by(Professional.id)
    )
    return result.scalars().all()

@router.get("/disputes", response_model=List[DisputeResponse])
async def list_disputes(
    status: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin lista as disputas, opcionalmente filtradas por status."""
    query = select(Dispute)
    if status:
        query = query.where(Dispute.status == status)
    query = query.order_by(Dispute.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.patch("/disputes/{dispute_id}", response_model=DisputeResponse)
async def resolve_dispute(
    dispute_id: UUID,
    payload: DisputeResolve,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin resolve uma disputa e executa o estorno financeiro correspondente."""
    from app.services import payment_service
    try:
        resolved = await payment_service.resolve_dispute_admin(
            db=db,
            admin_user_id=admin.id,
            dispute_id=dispute_id,
            resolution=payload.resolution,
            refund_percent=payload.refund_percent,
            admin_notes=payload.admin_notes
        )
        await db.commit()
        return resolved
    except HTTPException as e:
        raise e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

