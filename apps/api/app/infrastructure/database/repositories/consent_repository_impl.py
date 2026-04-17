from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.lgpd import ConsentLog
from app.domain.repositories.consent_repository import ConsentRepository
from app.models.lgpd import ConsentLog as ConsentLogModel

class ConsentRepositoryImpl(ConsentRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_all(self, consents: List[ConsentLog]) -> None:
        models = [
            ConsentLogModel(
                user_id=c.user_id,
                consent_type=c.consent_type,
                version=c.version,
                ip_address=c.ip_address,
                user_agent=c.user_agent,
                created_at=c.created_at
            )
            for c in consents
        ]
        self.db.add_all(models)
        await self.db.flush()
