import uuid
from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(
        UUID(as_uuid=True),
        ForeignKey("requests.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True
    )
    professional_id = Column(UUID(as_uuid=True), ForeignKey("professionals.id", ondelete="RESTRICT"), nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    
    status = Column(String(30), nullable=False, default="active") 
    # 'active' | 'payment_confirmed' | 'completed' | 'disputed' | 'refunded' | 'partially_refunded' | 'cancelled'
    
    agreed_cents = Column(Integer, nullable=False)

    professional = relationship("Professional", backref="contracts")
    client = relationship("User", backref="client_contracts")
