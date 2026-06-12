import uuid
from datetime import date
from sqlalchemy import Column, ForeignKey, Numeric, Date, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class CommissionRate(Base):
    __tablename__ = "commission_rates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=True
    )
    percent = Column(Numeric(5, 2), nullable=False)
    effective_from = Column(
        Date,
        nullable=False,
        default=date.today
    )
    effective_until = Column(Date, nullable=True)

    __table_args__ = (
        CheckConstraint("percent > 0 AND percent < 100", name="chk_comm_rates_percent"),
        CheckConstraint("effective_until IS NULL OR effective_until > effective_from", name="chk_comm_rates_dates"),
    )
