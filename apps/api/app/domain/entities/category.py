from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

class Category(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    color: Optional[str] = None
