"""Model SQLAlchemy para a tabela professionals."""
import uuid as _uuid

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text, Index, func
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.orm import relationship

from app.core.database import Base
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKBElement, WKTElement
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
        if not isinstance(self, Professional) or self.location is None:
            return None
        if isinstance(self.location, (WKBElement, WKTElement)):
            return to_shape(self.location).y
        if isinstance(self.location, str) and "POINT" in self.location:
            try:
                return float(self.location.split("(")[1].split(")")[0].split(" ")[1])
            except (IndexError, ValueError):
                return None
        return None

    @latitude.setter
    def latitude(self, value: float):
        if value is None:
            return
        current_long = self.longitude or 0.0
        self.location = f"POINT({current_long} {value})"

    @latitude.expression
    def latitude(cls):
        return func.ST_Y(cls.location)

    @hybrid_property
    def longitude(self) -> float:
        if not isinstance(self, Professional) or self.location is None:
            return None
        if isinstance(self.location, (WKBElement, WKTElement)):
            return to_shape(self.location).x
        if isinstance(self.location, str) and "POINT" in self.location:
            try:
                return float(self.location.split("(")[1].split(")")[0].split(" ")[0])
            except (IndexError, ValueError):
                return None
        return None

    @longitude.setter
    def longitude(self, value: float):
        if value is None:
            return
        current_lat = self.latitude or 0.0
        self.location = f"POINT({value} {current_lat})"

    @longitude.expression
    def longitude(cls):
        return func.ST_X(cls.location)

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

