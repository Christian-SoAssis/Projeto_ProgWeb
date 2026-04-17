import uuid
from typing import Optional
from app.domain.entities.request import Request
from app.domain.repositories.request_repository import RequestRepository
from app.domain.exceptions import EntityNotFoundError, BusinessRuleViolationError

class GetRequestUseCase:
    def __init__(self, request_repo: RequestRepository):
        self.request_repo = request_repo

    async def execute(self, request_id: uuid.UUID) -> Request:
        request = await self.request_repo.get_by_id(request_id)
        if not request:
            raise EntityNotFoundError("Request", request_id)
        return request
