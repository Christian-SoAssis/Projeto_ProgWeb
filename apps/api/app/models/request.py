from typing import List, Optional
from datetime import datetime
import uuid
from sqlalchemy import Column, ForeignKey, Text, Integer, DateTime, CheckConstraint, Boolean
from sqlalchemy.orm import Relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.hybrid import hybrid_property
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from app.core.database import Base


class Request(Base):
    __tablename__ = "requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    urgency = Column(Text, nullable=False)
    budget_cents = Column(Integer, nullable=True)
    status = Column(Text, nullable=False, server_default="open")
    
    # AI Fields
    ai_complexity = Column(Text, nullable=True)
    ai_urgency = Column(Text, nullable=True)
    ai_specialties = Column(ARRAY(Text), nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default="now()")
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default="now()", onupdate=datetime.now)

    @hybrid_property
    def latitude(self) -> float:
        if self.location is not None:
            point = to_shape(self.location)
            return point.y
        return None

    @hybrid_property
    def longitude(self) -> float:
        if self.location is not None:
            point = to_shape(self.location)
            return point.x
        return None

    # Relationships
    client = Relationship("User", back_populates="requests", lazy="noload")
    category = Relationship("Category", back_populates="requests", lazy="noload")
    images = Relationship("RequestImage", back_populates="request", cascade="all, delete-orphan", lazy="noload")
    bids = Relationship("Bid", back_populates="request", cascade="all, delete-orphan", lazy="noload")

    __table_args__ = (
        CheckConstraint("length(title) >= 5", name="chk_req_title_len"),
        CheckConstraint("urgency IN ('immediate','scheduled','flexible')", name="chk_req_urgency"),
        CheckConstraint("budget_cents > 0", name="chk_req_budget"),
        CheckConstraint("status IN ('open','matched','in_progress','done','cancelled')", name="chk_req_status"),
        CheckConstraint("ai_complexity IN ('simple','medium','complex')", name="chk_req_ai_complex"),
        CheckConstraint("ai_urgency IN ('low','medium','high')", name="chk_req_ai_urgency"),
    )


class RequestImage(Base):
    __tablename__ = "request_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("requests.id", ondelete="CASCADE"), nullable=False)
    url = Column(Text, nullable=False)
    content_type = Column(Text, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    analyzed = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default="now()")

    # Relationships
    request = Relationship("Request", back_populates="images")

    __table_args__ = (
        CheckConstraint("content_type IN ('image/jpeg','image/png','image/webp')", name="chk_req_img_content_type"),
        CheckConstraint("size_bytes > 0 AND size_bytes <= 10485760", name="chk_req_img_size"),
    )
