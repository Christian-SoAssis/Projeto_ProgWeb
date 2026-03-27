from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    color: str  # Hex (#RRGGBB) — vem do campo `color` da tabela categories
    parent_id: Optional[UUID]
    sort_order: int
    is_active: bool
    children: list["CategoryResponse"] = []

    model_config = {"from_attributes": True}


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., pattern=r"^[a-z0-9-]+$", max_length=100)
    color: str = Field("#1a9878", pattern=r"^#[0-9a-fA-F]{6}$")
    parent_id: Optional[UUID] = None
    sort_order: int = Field(0, ge=0)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    slug: Optional[str] = Field(None, pattern=r"^[a-z0-9-]+$")
    color: Optional[str] = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")
    parent_id: Optional[UUID] = None
    sort_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
