import uuid
from dataclasses import dataclass
from typing import Optional

from app.domain.entities.user import User, UserRole
from app.domain.entities.lgpd import ConsentLog
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.consent_repository import ConsentRepository
from app.domain.exceptions import BusinessRuleViolationError
from app.core.security import hash_password
from app.core.config import settings

@dataclass
class RegisterClientInput:
    name: str
    email: str
    phone: Optional[str]
    password: str
    ip_address: str
    user_agent: str

class RegisterClientUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        consent_repo: ConsentRepository
    ):
        self.user_repo = user_repo
        self.consent_repo = consent_repo

    async def execute(self, input_data: RegisterClientInput) -> User:
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
            role=UserRole.CLIENT,
            is_active=True
        )

        # 3. Criar Consentimentos
        consents = [
            ConsentLog(
                user_id=user_id,
                consent_type="terms",
                version=settings.TERMS_VERSION,
                is_granted=True,
                ip_address=input_data.ip_address,
                user_agent=input_data.user_agent
            ),
            ConsentLog(
                user_id=user_id,
                consent_type="privacy",
                version=settings.TERMS_VERSION,
                is_granted=True,
                ip_address=input_data.ip_address,
                user_agent=input_data.user_agent
            )
        ]

        # 4. Salvar
        await self.user_repo.save(user)
        await self.consent_repo.save_all(consents)

        return user
