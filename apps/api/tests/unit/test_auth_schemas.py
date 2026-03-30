import pytest
from pydantic import ValidationError
from uuid import uuid4

from app.schemas.auth import (
    UserCreate,
    ProfessionalCreate,
    UserUpdate,
    LoginRequest,
    RefreshRequest,
    DeleteAccountRequest,
    ConsentPayload
)

def test_user_create_invalid():
    # name vazio
    with pytest.raises(ValidationError):
        UserCreate(name="", email="test@b.com", password="12345678", consent_terms=True, consent_privacy=True)
    # name curto
    with pytest.raises(ValidationError):
        UserCreate(name="a", email="test@b.com", password="12345678", consent_terms=True, consent_privacy=True)
    # name longo
    with pytest.raises(ValidationError):
        UserCreate(name="x"*101, email="test@b.com", password="12345678", consent_terms=True, consent_privacy=True)
    # email invalido
    with pytest.raises(ValidationError):
        UserCreate(name="Joao", email="nao-e-email", password="12345678", consent_terms=True, consent_privacy=True)
    # email sem arroba
    with pytest.raises(ValidationError):
        UserCreate(name="Joao", email="sem-arroba", password="12345678", consent_terms=True, consent_privacy=True)
    # phone curto sem +55
    with pytest.raises(ValidationError):
        UserCreate(name="Joao", email="test@b.com", phone="11999887766", password="12345678", consent_terms=True, consent_privacy=True)
    # phone letras
    with pytest.raises(ValidationError):
        UserCreate(name="Joao", email="test@b.com", phone="+5511a99887766", password="12345678", consent_terms=True, consent_privacy=True)
    # password curto
    with pytest.raises(ValidationError):
        UserCreate(name="Joao", email="test@b.com", password="1234567", consent_terms=True, consent_privacy=True)
    # consent terms false
    with pytest.raises(ValidationError):
        UserCreate(name="Joao", email="test@b.com", password="12345678", consent_terms=False, consent_privacy=True)

def test_professional_create_invalid():
    base_data = dict(name="Bia", email="test@test.com", password="password123", consent_terms=True, consent_privacy=True)
    # lat/long fora
    with pytest.raises(ValidationError):
        ProfessionalCreate(**base_data, document_type="cpf", latitude=91.0, longitude=0.0, service_radius_km=10.0, category_ids=[uuid4()])
    with pytest.raises(ValidationError):
        ProfessionalCreate(**base_data, document_type="cpf", latitude=-91.0, longitude=0.0, service_radius_km=10.0, category_ids=[uuid4()])
    with pytest.raises(ValidationError):
        ProfessionalCreate(**base_data, document_type="cpf", latitude=0.0, longitude=181.0, service_radius_km=10.0, category_ids=[uuid4()])
    # radius_km invalido
    with pytest.raises(ValidationError):
        ProfessionalCreate(**base_data, document_type="cpf", latitude=0.0, longitude=0.0, service_radius_km=0.0, category_ids=[uuid4()])
    with pytest.raises(ValidationError):
        ProfessionalCreate(**base_data, document_type="cpf", latitude=0.0, longitude=0.0, service_radius_km=-5.0, category_ids=[uuid4()])
    with pytest.raises(ValidationError):
        ProfessionalCreate(**base_data, document_type="cpf", latitude=0.0, longitude=0.0, service_radius_km=201.0, category_ids=[uuid4()])
    # hourly rate invalido
    with pytest.raises(ValidationError):
        ProfessionalCreate(**base_data, document_type="cpf", latitude=0.0, longitude=0.0, service_radius_km=10.0, category_ids=[uuid4()], hourly_rate_cents=0)
    with pytest.raises(ValidationError):
        ProfessionalCreate(**base_data, document_type="cpf", latitude=0.0, longitude=0.0, service_radius_km=10.0, category_ids=[uuid4()], hourly_rate_cents=-100)
    # category ids
    with pytest.raises(ValidationError):
        ProfessionalCreate(**base_data, document_type="cpf", latitude=0.0, longitude=0.0, service_radius_km=10.0, category_ids=[])
    with pytest.raises(ValidationError):
        ProfessionalCreate(**base_data, document_type="cpf", latitude=0.0, longitude=0.0, service_radius_km=10.0, category_ids=[uuid4()]*11)
    # bio > 1000
    with pytest.raises(ValidationError):
        ProfessionalCreate(**base_data, document_type="cpf", latitude=0.0, longitude=0.0, service_radius_km=10.0, category_ids=[uuid4()], bio="x"*1001)
    # auth_type
    with pytest.raises(ValidationError):
        ProfessionalCreate(**base_data, document_type="rg", latitude=0.0, longitude=0.0, service_radius_km=10.0, category_ids=[uuid4()])

def test_user_update_invalid():
    with pytest.raises(ValidationError):
        UserUpdate(name="x")
    with pytest.raises(ValidationError):
        UserUpdate(name="x"*101)
    with pytest.raises(ValidationError):
        UserUpdate(phone="11999")

def test_login_request_invalid():
    with pytest.raises(ValidationError):
        LoginRequest(email="invalido", password="abc")
    with pytest.raises(ValidationError):
        LoginRequest(email="a@b.com", password="")

def test_refresh_request_invalid():
    with pytest.raises(ValidationError):
        RefreshRequest(refresh_token="")

def test_delete_account_request_invalid():
    with pytest.raises(ValidationError):
        DeleteAccountRequest(password="")

def test_consent_payload_invalid():
    with pytest.raises(ValidationError):
        ConsentPayload(consent_terms=False, consent_privacy=True)
    with pytest.raises(ValidationError):
        ConsentPayload(consent_terms=True, consent_privacy=False)
