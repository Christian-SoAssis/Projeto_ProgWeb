import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

class Bid(Base):
    __tablename__ = "bids"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), nullable=False) # FK to requests will be in Module 3
    professional_id = Column(UUID(as_uuid=True), ForeignKey("professionals.id", ondelete="CASCADE"), nullable=False)
    price_cents = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="pending") # 'pending' | 'accepted' | 'rejected' | 'cancelled'
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    professional = relationship("Professional", backref="bids")

    __table_args__ = (
        UniqueConstraint("request_id", "professional_id", name="uq_request_professional_bid"),
    )
