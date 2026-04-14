"""Model SQLAlchemy para a tabela professionals."""
import uuid as _uuid

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.orm import relationship

from app.core.database import Base
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from shapely.geometry import Point
from sqlalchemy.ext.hybrid import hybrid_property

from app.models.associations import professional_categories


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

    # Localização via PostGIS
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)

    @hybrid_property
    def latitude(self) -> float:
        if isinstance(self, Professional) and self.location is not None:
            point = to_shape(self.location)
            return point.y
        return None

    @latitude.setter
    def latitude(self, value: float):
        if self.location is None:
            self.location = f"POINT({self.longitude or 0.0} {value})"
        else:
            p = to_shape(self.location)
            self.location = f"POINT({p.x} {value})"

    @hybrid_property
    def longitude(self) -> float:
        if isinstance(self, Professional) and self.location is not None:
            point = to_shape(self.location)
            return point.x
        return None

    @longitude.setter
    def longitude(self, value: float):
        if self.location is None:
            self.location = f"POINT({value} {self.latitude or 0.0})"
        else:
            p = to_shape(self.location)
            self.location = f"POINT({value} {p.y})"

    service_radius_km = Column(Float, nullable=False, default=20.0)
    hourly_rate_cents = Column(Integer, nullable=True)
    reputation_score = Column(Float, nullable=False, default=0.0)
    is_verified = Column(Boolean, nullable=False, default=False)
    rejection_reason = Column(String(500), nullable=True)

    # Caminho do documento enviado (CPF/CNPJ)
    document_path = Column(String(500), nullable=True)
    document_type = Column(String(10), nullable=True)  # 'cpf' | 'cnpj'

    # Indice FTS (tsvector)
    search_vector = Column(TSVECTOR, nullable=True)

    # Relacionamentos
    user = relationship("User", back_populates="professional", lazy="noload")
    categories = relationship(
        "Category",
        secondary=professional_categories,
        back_populates="professionals",
        lazy="noload",
    )

