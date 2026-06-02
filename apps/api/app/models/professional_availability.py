import uuid
from sqlalchemy import Column, ForeignKey, Integer, Time, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class ProfessionalAvailability(Base):
    __tablename__ = "professional_availabilities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    professional_id = Column(
        UUID(as_uuid=True),
        ForeignKey("professionals.id", ondelete="CASCADE"),
        nullable=False,
    )
    day_of_week = Column(Integer, nullable=False)  # 0 = Sunday, 1 = Monday, ..., 6 = Saturday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint("professional_id", "day_of_week", name="uq_professional_day_availability"),
    )

    professional = relationship("Professional", lazy="noload")
