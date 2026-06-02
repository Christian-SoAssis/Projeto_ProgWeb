from pydantic import BaseModel, Field, field_validator
from typing import List, Literal
from uuid import UUID
from datetime import time, date
import re


class ProfessionalPixKeyCreate(BaseModel):
    key_type: Literal["cpf", "cnpj", "email", "phone", "random"]
    key_value: str = Field(..., max_length=100)

    @field_validator("key_value")
    @classmethod
    def validate_key_value(cls, v: str, info) -> str:
        key_type = info.data.get("key_type")
        if not key_type:
            return v
        
        v_clean = v.strip()
        
        if key_type == "cpf":
            cpf_digits = re.sub(r"\D", "", v_clean)
            if len(cpf_digits) != 11:
                raise ValueError("CPF Pix key must have 11 digits")
            return cpf_digits
            
        elif key_type == "cnpj":
            cnpj_digits = re.sub(r"\D", "", v_clean)
            if len(cnpj_digits) != 14:
                raise ValueError("CNPJ Pix key must have 14 digits")
            return cnpj_digits
            
        elif key_type == "phone":
            phone_digits = re.sub(r"\D", "", v_clean)
            # Accept phones starting with +55 or without country code, usually 10-13 digits
            if not (10 <= len(phone_digits) <= 13):
                raise ValueError("Phone Pix key must be a valid number with DDD")
            return f"+{phone_digits}" if not v_clean.startswith("+") else v_clean
            
        elif key_type == "email":
            email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            if not re.match(email_pattern, v_clean):
                raise ValueError("Email Pix key must be a valid email address")
            return v_clean.lower()
            
        elif key_type == "random":
            # Random keys are usually UUIDs
            uuid_pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
            if not re.match(uuid_pattern, v_clean):
                raise ValueError("Random Pix key must be a valid UUID key format")
            return v_clean.lower()
            
        return v


class ProfessionalPixKeyResponse(BaseModel):
    id: UUID
    professional_id: UUID
    key_type: str
    key_value: str
    is_active: bool

    class Config:
        from_attributes = True


class ProfessionalAvailabilityDay(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="0 = Sunday, 1 = Monday, ..., 6 = Saturday")
    start_time: time
    end_time: time
    is_active: bool = True

    @field_validator("end_time")
    @classmethod
    def validate_times(cls, end_time: time, info) -> time:
        start_time = info.data.get("start_time")
        if start_time and end_time <= start_time:
            raise ValueError("end_time must be after start_time")
        return end_time


class ProfessionalAvailabilityCreate(BaseModel):
    availabilities: List[ProfessionalAvailabilityDay]


class ProfessionalAvailabilityResponse(BaseModel):
    availabilities: List[ProfessionalAvailabilityDay]


class AvailableSlotResponse(BaseModel):
    start_time: str  # Format "HH:MM"
    end_time: str    # Format "HH:MM"
