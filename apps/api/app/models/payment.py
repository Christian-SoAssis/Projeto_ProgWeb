import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contracts.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    amount_cents = Column(Integer, nullable=False)
    fee_cents = Column(Integer, nullable=False)
    professional_amount_cents = Column(Integer, nullable=False)
    status = Column(String(30), nullable=False, default="pending", index=True)
    mp_preference_id = Column(String(100), nullable=True, index=True)
    mp_payment_id = Column(String(100), nullable=True, unique=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    contract = relationship("Contract", lazy="noload")
    disputes = relationship("Dispute", back_populates="payment", lazy="noload")


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="RESTRICT"),
        nullable=True,
    )
    contract_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contracts.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    opened_by_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    reason = Column(String(500), nullable=False)
    category = Column(String(50), nullable=False)
    status = Column(String(30), nullable=False, default="opened", index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    payment = relationship("Payment", back_populates="disputes", lazy="noload")
    opened_by = relationship("User", foreign_keys=[opened_by_user_id], lazy="noload")
    contract = relationship("Contract", lazy="noload")
