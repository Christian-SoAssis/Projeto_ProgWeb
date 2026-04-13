from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class MatchResponse(BaseModel):
    """Profissional rankeado retornado pelo endpoint de matching."""
    id: UUID
    user_id: UUID
    bio: str
    latitude: float
    longitude: float
    service_radius_km: float
    hourly_rate_cents: Optional[int] = None
    reputation_score: float
    is_verified: bool
    distance_km: float = Field(..., ge=0, description="Distância em km até o pedido")

    model_config = ConfigDict(from_attributes=True)
