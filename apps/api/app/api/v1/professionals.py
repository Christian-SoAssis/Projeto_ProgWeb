import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from pydantic import ValidationError

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
