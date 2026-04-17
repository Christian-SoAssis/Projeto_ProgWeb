import uuid
from dataclasses import dataclass
from typing import List, Optional
from fastapi import UploadFile

from app.domain.entities.user import User, UserRole
from app.domain.entities.professional import Professional
from app.domain.entities.lgpd import ConsentLog
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.professional_repository import ProfessionalRepository
from app.domain.repositories.consent_repository import ConsentRepository
from app.domain.services.image_storage import ImageStorage
from app.domain.exceptions import BusinessRuleViolationError
from app.core.security import hash_password
from app.core.config import settings

@dataclass
class RegisterProfessionalInput:
    name: str
    email: str
    phone: Optional[str]
    password: str
    bio: str
    latitude: float
    longitude: float
    service_radius_km: float
    hourly_rate_cents: int
    category_ids: List[uuid.UUID]
    document_type: str
    document: UploadFile
    ip_address: Optional[str]
    user_agent: Optional[str]

class RegisterProfessionalUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        prof_repo: ProfessionalRepository,
        consent_repo: ConsentRepository,
        file_storage: ImageStorage
    ):
        self.user_repo = user_repo
        self.prof_repo = prof_repo
        self.consent_repo = consent_repo
        self.file_storage = file_storage

    async def execute(self, input_data: RegisterProfessionalInput) -> Professional:
        # 1. Validar se email já existe
        existing_user = await self.user_repo.get_by_email(input_data.email)
        if existing_user:
            raise BusinessRuleViolationError("Email já cadastrado")

        # 2. Criar Usuário
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            name=input_data.name,
            email=input_data.email,
            phone=input_data.phone,
            password_hash=hash_password(input_data.password),
            role=UserRole.PROFESSIONAL,
            is_active=True
        )

        # 3. Criar Consentimentos
        consents = [
            ConsentLog(
                user_id=user_id,
                consent_type="terms",
                version=settings.TERMS_VERSION,
                ip_address=input_data.ip_address,
                user_agent=input_data.user_agent
            ),
            ConsentLog(
                user_id=user_id,
                consent_type="privacy",
                version=settings.TERMS_VERSION,
                ip_address=input_data.ip_address,
                user_agent=input_data.user_agent
            )
        ]

        # 4. Salvar Documento
        # Reutilizando ImageStorage interface (LocalImageStorage suporta qualquer UploadFile)
        document_path = await self.file_storage.save_image(input_data.document)

        # 5. Criar Perfil Profissional
        professional = Professional(
            id=uuid.uuid4(),
            user_id=user_id,
            bio=input_data.bio,
            latitude=input_data.latitude,
            longitude=input_data.longitude,
            service_radius_km=input_data.service_radius_km,
            hourly_rate_cents=input_data.hourly_rate_cents,
            document_type=input_data.document_type,
            document_path=document_path,
            is_verified=False,
            name=input_data.name, # Para facilitar resposta
            email=input_data.email
        )

        # 6. Persistência (O ideal é ser atômico no repo ou via UoW)
        await self.user_repo.save(user)
        await self.consent_repo.save_all(consents)
        saved_prof = await self.prof_repo.save(professional)

        return saved_prof
