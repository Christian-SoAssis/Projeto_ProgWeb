import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request, Query
from pydantic import ValidationError
from datetime import date
from typing import List
from app.schemas.v1.availability import AvailableSlotResponse
from app.core.dependencies import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_register_professional_use_case, get_professional_use_case
from app.application.use_cases.register_professional_use_case import RegisterProfessionalUseCase, RegisterProfessionalInput
from app.application.use_cases.get_professional_use_case import GetProfessionalUseCase
from app.domain.exceptions import BusinessRuleViolationError, EntityNotFoundError
from app.schemas.v1.auth import (
    ProfessionalRegisterResponse,
)
from app.schemas.v1.professionals import ProfessionalPublicProfile

router = APIRouter(prefix="/professionals", tags=["Professionals"])


@router.post("/", response_model=ProfessionalRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_professional(
    request: Request,
    # Multipart fields
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    password: str = Form(...),
    consent_terms: bool = Form(...),
    consent_privacy: bool = Form(...),
    
    # Professional fields
    bio: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    service_radius_km: float = Form(...),
    hourly_rate_cents: int = Form(...),
    category_ids_json: str = Form(..., description="JSON array de UUIDs de categoria"),
    document_type: str = Form(...),
    
    # Upload
    document: UploadFile = File(...),
    
    register_use_case: RegisterProfessionalUseCase = Depends(get_register_professional_use_case)
):
    """Cadastro completo de profissional via Use Case."""
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "unknown")

    try:
        category_ids = [UUID(cid) for cid in json.loads(category_ids_json)]
        
        input_data = RegisterProfessionalInput(
            name=name, email=email, phone=phone, password=password,
            bio=bio, latitude=latitude, longitude=longitude,
            service_radius_km=service_radius_km, hourly_rate_cents=hourly_rate_cents,
            category_ids=category_ids, document_type=document_type,
            document=document, ip_address=ip, user_agent=ua
        )
        
        professional = await register_use_case.execute(input_data)
        
        # O mapper to_entity já traz os campos necessários do User se carregado
        # Para a resposta, precisamos de um objeto que o FromProfessional entenda ou adaptar o schema
        return ProfessionalRegisterResponse.from_professional_entity(professional)
        
    except (ValidationError, json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        print(f"Error registering professional: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{professional_id}", response_model=ProfessionalPublicProfile)
async def get_professional_profile(
    professional_id: UUID,
    get_use_case: GetProfessionalUseCase = Depends(get_professional_use_case)
):
    """Retorna o perfil público de um profissional por ID via Use Case."""
    try:
        professional = await get_use_case.execute(professional_id)
        
        return {
            "id": professional.id,
            "name": professional.name,
            "bio": professional.bio,
            "reputation_score": professional.reputation_score,
            "is_verified": professional.is_verified,
            "hourly_rate_cents": professional.hourly_rate_cents,
            "categories": [
                {"id": cat.id, "name": cat.name, "color": cat.color}
                for cat in professional.categories
            ]
        }
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{professional_id}/available-slots", response_model=List[AvailableSlotResponse])
async def get_available_slots(
    professional_id: UUID,
    date_query: date = Query(..., alias="date"),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select
    from datetime import datetime, time, timedelta, timezone
    from app.models.professional import Professional
    from app.models.professional_availability import ProfessionalAvailability
    from app.models.contract import Contract

    # 1. Verificar se o profissional existe
    result = await db.execute(select(Professional).where(Professional.id == professional_id))
    professional = result.scalar_one_or_none()
    if not professional:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")

    # 2. Obter dia da semana (0 = Sunday, 1 = Monday, ..., 6 = Saturday)
    # Python weekday(): 0 = Monday, 6 = Sunday.
    py_weekday = date_query.weekday()
    day_of_week = (py_weekday + 1) % 7

    # 3. Obter grade horária semanal
    result = await db.execute(
        select(ProfessionalAvailability)
        .where(ProfessionalAvailability.professional_id == professional_id)
        .where(ProfessionalAvailability.day_of_week == day_of_week)
        .where(ProfessionalAvailability.is_active == True)
    )
    availability = result.scalar_one_or_none()
    if not availability:
        return []  # Não atende nesse dia

    start_time = availability.start_time
    end_time = availability.end_time

    # 4. Obter contratos ativos agendados para este dia (UTC)
    start_of_day = datetime.combine(date_query, time.min).replace(tzinfo=timezone.utc)
    end_of_day = datetime.combine(date_query, time.max).replace(tzinfo=timezone.utc)

    result = await db.execute(
        select(Contract)
        .where(Contract.professional_id == professional_id)
        .where(Contract.status.in_(["active", "payment_confirmed"]))
        .where(Contract.scheduled_start >= start_of_day)
        .where(Contract.scheduled_start <= end_of_day)
    )
    contracts = result.scalars().all()

    # 5. Gerar slots de 1 hora
    slots = []
    current_dt = datetime.combine(date_query, start_time)
    end_dt = datetime.combine(date_query, end_time)

    # Margem de buffer: 1 hora
    buffer = timedelta(hours=1)

    while current_dt + timedelta(hours=1) <= end_dt:
        slot_start = current_dt
        slot_end = current_dt + timedelta(hours=1)

        # Verificar interseção com contratos existentes
        has_conflict = False
        for contract in contracts:
            if not contract.scheduled_start:
                continue
            
            # Obter início e fim do contrato em timezone naive (local do dia da query)
            # Como salvamos em UTC, vamos converter ou assumir naive para comparação
            c_start = contract.scheduled_start.replace(tzinfo=None)
            c_end = contract.scheduled_end.replace(tzinfo=None) if contract.scheduled_end else c_start + timedelta(hours=1)

            # Janela de conflito inclui buffer (1 hora antes e 1 hora depois)
            conflict_start = c_start - buffer
            conflict_end = c_end + buffer

            # Verificar se slot se sobrepõe
            if max(slot_start, conflict_start) < min(slot_end, conflict_end):
                has_conflict = True
                break

        if not has_conflict:
            slots.append(
                AvailableSlotResponse(
                    start_time=slot_start.strftime("%H:%M"),
                    end_time=slot_end.strftime("%H:%M")
                )
            )

        current_dt += timedelta(hours=1)

    return slots
