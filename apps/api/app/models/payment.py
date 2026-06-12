import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Text, ARRAY
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
    reason = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    evidence_urls = Column(ARRAY(Text), nullable=False, default=list, server_default='{}')
    status = Column(String(30), nullable=False, default="opened", index=True)
    resolution = Column(String(30), nullable=True)
    refund_percent = Column(Integer, nullable=True)
    admin_notes = Column(Text, nullable=True)
    response_message = Column(Text, nullable=True)
    response_evidence_urls = Column(ARRAY(Text), nullable=True, default=list, server_default='{}')
    proposed_resolution = Column(Text, nullable=True)
    response_deadline = Column(DateTime(timezone=True), nullable=False)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    payment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="RESTRICT"),
        nullable=True,
    )

    payment = relationship("Payment", back_populates="disputes", lazy="noload")
    opened_by = relationship("User", foreign_keys=[opened_by_user_id], lazy="noload")
    contract = relationship("Contract", lazy="noload")

