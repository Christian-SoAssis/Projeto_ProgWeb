import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True),
                        ForeignKey("requests.id", ondelete="RESTRICT"),
                        nullable=False, unique=True)
    professional_id = Column(UUID(as_uuid=True),
                             ForeignKey("professionals.id", ondelete="RESTRICT"),
                             nullable=False)
    client_id = Column(UUID(as_uuid=True),
                       ForeignKey("users.id", ondelete="RESTRICT"),
                       nullable=False)
    agreed_cents = Column(Integer, nullable=False)
    status = Column(String(30), nullable=False, default="active")
    started_at = Column(DateTime(timezone=True),
                        default=lambda: datetime.now(timezone.utc),
                        nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    professional = relationship("Professional", lazy="noload")
    client = relationship("User", lazy="noload")
    request = relationship("Request", lazy="noload")
