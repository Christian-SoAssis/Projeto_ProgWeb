import uuid
from typing import List, Optional
from app.domain.entities.request import Request
from app.domain.repositories.request_repository import RequestRepository

class ListRequestsUseCase:
    def __init__(self, request_repo: RequestRepository):
        self.request_repo = request_repo

    async def execute(
        self, 
        client_id: Optional[uuid.UUID] = None, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Request]:
        return await self.request_repo.list(client_id=client_id, limit=limit, offset=offset)
