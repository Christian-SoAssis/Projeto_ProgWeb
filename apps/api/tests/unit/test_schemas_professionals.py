import pytest
from uuid import uuid4
from pydantic import ValidationError
from app.schemas.v1.professionals import ProfessionalCreate, ProfessionalResponse, ProfessionalApproval

def test_professional_create_valid():
    """Testa criação válida de profissional."""
    data = {
        "bio": "Profissional com 10 anos de experiência em reformas residenciais.",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "service_radius_km": 50.0,
        "hourly_rate_cents": 15000,
        "category_ids": [uuid4()],
        "document_type": "cpf"
    }
    prof = ProfessionalCreate(**data)
    assert prof.bio == data["bio"]
    assert prof.document_type == "cpf"

def test_professional_create_invalid_bio():
    """Testa bio muito curta."""
    data = {
        "bio": "Curta",
        "latitude": 0,
        "longitude": 0,
        "service_radius_km": 10,
        "hourly_rate_cents": 1000,
        "category_ids": [uuid4()],
        "document_type": "cpf"
    }
    with pytest.raises(ValidationError):
        ProfessionalCreate(**data)

def test_professional_create_invalid_coords():
    """Testa coordenadas inválidas."""
    base_data = {
        "bio": "Bio válida com mais de dez caracteres.",
        "service_radius_km": 10,
        "hourly_rate_cents": 1000,
        "category_ids": [uuid4()],
        "document_type": "cpf"
    }
    # Latitude out of range
    with pytest.raises(ValidationError):
        ProfessionalCreate(latitude=91, longitude=0, **base_data)
    
    # Longitude out of range
    with pytest.raises(ValidationError):
        ProfessionalCreate(latitude=0, longitude=181, **base_data)

def test_professional_create_invalid_radius():
    """Testa raio de serviço inválido."""
    base_data = {
        "bio": "Bio válida com mais de dez caracteres.",
        "latitude": 0,
        "longitude": 0,
        "hourly_rate_cents": 1000,
        "category_ids": [uuid4()],
        "document_type": "cpf"
    }
    # Zero radius
    with pytest.raises(ValidationError):
        ProfessionalCreate(service_radius_km=0, **base_data)
    
    # Negative radius
    with pytest.raises(ValidationError):
        ProfessionalCreate(service_radius_km=-1, **base_data)
    
    # Radius > 200
    with pytest.raises(ValidationError):
        ProfessionalCreate(service_radius_km=201, **base_data)

def test_professional_create_invalid_categories():
    """Testa lista de categorias inválida."""
    base_data = {
        "bio": "Bio válida com mais de dez caracteres.",
        "latitude": 0,
        "longitude": 0,
        "service_radius_km": 10,
        "hourly_rate_cents": 1000,
        "document_type": "cpf"
    }
    # Empty list
    with pytest.raises(ValidationError):
        ProfessionalCreate(category_ids=[], **base_data)
    
    # Too many items (11)
    with pytest.raises(ValidationError):
        ProfessionalCreate(category_ids=[uuid4() for _ in range(11)], **base_data)

def test_professional_create_invalid_doc_type():
    """Testa tipo de documento inválido."""
    data = {
        "bio": "Bio válida com mais de dez caracteres.",
        "latitude": 0,
        "longitude": 0,
        "service_radius_km": 10,
        "hourly_rate_cents": 1000,
        "category_ids": [uuid4()],
        "document_type": "rg"
    }
    with pytest.raises(ValidationError):
        ProfessionalCreate(**data)

def test_professional_response_from_attributes():
    """Testa construção do response a partir de atributos (ORM)."""
    class MockProfessional:
        def __init__(self):
            self.id = uuid4()
            self.user_id = uuid4()
            self.bio = "Bio do profissional de teste."
            self.service_radius_km = 15.5
            self.hourly_rate_cents = 20000
            self.reputation_score = 4.8
            self.is_verified = True

    mock_prof = MockProfessional()
    resp = ProfessionalResponse.model_validate(mock_prof)
    assert resp.id == mock_prof.id
    assert resp.reputation_score == 4.8

def test_professional_approval_valid():
    """Testa schema de aprovação."""
    # Aprovação
    appr = ProfessionalApproval(is_verified=True)
    assert appr.is_verified is True
    assert appr.rejection_reason is None

    # Rejeição com motivo
    rejection = ProfessionalApproval(is_verified=False, rejection_reason="Documento ilegível")
    assert rejection.is_verified is False
    assert rejection.rejection_reason == "Documento ilegível"

def test_professional_approval_invalid_reason():
    """Testa motivo de rejeição muito longo."""
    long_reason = "a" * 501
    with pytest.raises(ValidationError):
        ProfessionalApproval(is_verified=False, rejection_reason=long_reason)
