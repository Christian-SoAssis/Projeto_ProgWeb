import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True),
                       ForeignKey("users.id", ondelete="CASCADE"),
                       nullable=False)
    professional_id = Column(UUID(as_uuid=True),
                             ForeignKey("professionals.id", ondelete="CASCADE"),
                             nullable=False)
    created_at = Column(DateTime(timezone=True),
                        default=lambda: datetime.now(timezone.utc),
                        nullable=False)

    professional = relationship("Professional", lazy="noload")

    __table_args__ = (
        UniqueConstraint("client_id", "professional_id",
                         name="uq_favorites_client_professional"),
    )
