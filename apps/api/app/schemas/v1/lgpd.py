from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, ConfigDict, IPvAnyAddress

class ConsentPayload(BaseModel):
    """Payload para registro ou atualização de consentimento."""
    consent_terms: bool = Field(...)
    consent_privacy: bool = Field(...)

    @field_validator("consent_terms")
    @classmethod
    def validate_terms(cls, v: bool) -> bool:
        if v is not True:
            raise ValueError("Aceite obrigatório dos termos")
        return v

    @field_validator("consent_privacy")
    @classmethod
    def validate_privacy(cls, v: bool) -> bool:
        if v is not True:
            raise ValueError("Aceite obrigatório da política de privacidade")
        return v

class ConsentResponse(BaseModel):
    """Resposta com histórico de consentimento."""
    id: UUID
    consent_type: str
    version: str
    accepted_at: datetime
    ip_address: Optional[IPvAnyAddress] = None
    user_agent: str

    model_config = ConfigDict(from_attributes=True)
