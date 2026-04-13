import uuid
from sqlalchemy import Column, ForeignKey, Integer, Table, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

# Tabela associativa many-to-many entre Professional e Category
professional_categories = Table(
    "professional_categories",
    Base.metadata,
    Column(
        "professional_id",
        UUID(as_uuid=True),
        ForeignKey("professionals.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "category_id",
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("years_experience", Integer, nullable=True),
    Column("is_primary", Boolean, nullable=False, server_default="false"),
)
