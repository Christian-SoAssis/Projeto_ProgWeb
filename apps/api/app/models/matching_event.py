import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class MatchingEvent(Base):
    __tablename__ = "matching_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(20), nullable=False)  # 'impression', 'conversion'
    request_id = Column(UUID(as_uuid=True),
                        ForeignKey("requests.id", ondelete="CASCADE"),
                        nullable=False)
    professional_id = Column(UUID(as_uuid=True),
                             ForeignKey("professionals.id", ondelete="CASCADE"),
                             nullable=False)
    bid_id = Column(UUID(as_uuid=True),
                    ForeignKey("bids.id", ondelete="SET NULL"),
                    nullable=True)
    position = Column(Integer, nullable=True)
    features = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True),
                        default=lambda: datetime.now(timezone.utc),
                        nullable=False)

    request = relationship("Request", lazy="noload")
    professional = relationship("Professional", lazy="noload")
    bid = relationship("Bid", lazy="noload")
