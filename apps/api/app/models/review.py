import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True),
                         ForeignKey("contracts.id", ondelete="RESTRICT"),
                         nullable=False, unique=True)
    reviewer_id = Column(UUID(as_uuid=True),
                         ForeignKey("users.id", ondelete="CASCADE"),
                         nullable=False)
    reviewee_id = Column(UUID(as_uuid=True),
                         ForeignKey("users.id", ondelete="CASCADE"),
                         nullable=False)
    rating = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    score_punctuality = Column(Float, nullable=True)
    score_quality = Column(Float, nullable=True)
    score_cleanliness = Column(Float, nullable=True)
    score_communication = Column(Float, nullable=True)
    is_authentic = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime(timezone=True),
                        default=lambda: datetime.now(timezone.utc),
                        nullable=False)

    contract = relationship("Contract", lazy="noload")
    reviewer = relationship("User", foreign_keys=[reviewer_id], lazy="noload")
    reviewee = relationship("User", foreign_keys=[reviewee_id], lazy="noload")
