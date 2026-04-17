from dataclasses import dataclass
from datetime import datetime, timezone
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.domain.exceptions import UnauthorizedError
from app.core.security import verify_password

@dataclass
class LoginInput:
    email: str
    password: str

class LoginUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, input_data: LoginInput) -> User:
        user = await self.user_repo.get_by_email(input_data.email)
        
        if not user or not verify_password(input_data.password, user.password_hash) or not user.is_active:
            raise UnauthorizedError("Credenciais inválidas")
        
        # O User repository implementation deve lidar com o update do last_login se quisermos
        # Ou podemos atualizar aqui e salvar
        # user.last_login_at = datetime.now(timezone.utc)
        # await self.user_repo.save(user)
        
        return user
