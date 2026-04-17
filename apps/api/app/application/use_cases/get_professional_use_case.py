from uuid import UUID
from typing import Optional
from app.domain.entities.professional import Professional
from app.domain.repositories.professional_repository import ProfessionalRepository
from app.domain.exceptions import NotFoundError

class GetProfessionalUseCase:
    def __init__(self, prof_repo: ProfessionalRepository):
        self.prof_repo = prof_repo

    async def execute(self, professional_id: UUID) -> Professional:
        professional = await self.prof_repo.get_by_id(professional_id)
        if not professional:
            raise NotFoundError("Profissional não encontrado")
        return professional
