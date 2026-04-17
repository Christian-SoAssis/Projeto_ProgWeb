from dataclasses import dataclass
from uuid import UUID
from typing import Optional

@dataclass
class Category:
    id: UUID
    name: str
    slug: Optional[str] = None
    color: Optional[str] = None
