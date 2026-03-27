"""Model SQLAlchemy para a tabela professionals."""
import uuid as _uuid

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Professional(Base):
    __tablename__ = "professionals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    bio = Column(Text, nullable=False)

    # Localização (lat/lng armazenados direto por simplicidade no Módulo 2;
    # PostGIS geometry é adicionado nas migrations futuras do Módulo 1.4.2)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    service_radius_km = Column(Float, nullable=False, default=20.0)
    hourly_rate_cents = Column(Integer, nullable=True)
    reputation_score = Column(Float, nullable=False, default=0.0)
    is_verified = Column(Boolean, nullable=False, default=False)
    rejection_reason = Column(String(500), nullable=True)

    # Caminho do documento enviado (CPF/CNPJ)
    document_path = Column(String(500), nullable=True)
    document_type = Column(String(10), nullable=True)  # 'cpf' | 'cnpj'

    # Relacionamentos
    user = relationship("User", back_populates="professional")
