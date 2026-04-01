import pytest
from pydantic import ValidationError
from uuid import uuid4

# Importação antecipada (falhará até que os schemas sejam criados/atualizados)
try:
    from app.schemas.v1.auth import UserCreate, ProfessionalCreate, LoginRequest, RefreshRequest, DeleteAccountRequest
    from app.schemas.v1.lgpd import ConsentPayload
except ImportError:
    # Definir stubs temporários apenas para permitir que o arquivo de teste exista
    # e falhe de forma controlada ou para que eu possa escrever o teste agora.
    # Na prática, o TDD espera que o teste falhe porque o código não existe.
    pass

def test_user_create_schema_validation():
    """Testa validações do schema UserCreate."""
    # Caso válido
    valid_data = {
        "name": "João Silva",
        "email": "JOAO@exemplo.com",
        "phone": "+5511999999999",
        "password": "password123",
        "consent_terms": True,
        "consent_privacy": True
    }
    user = UserCreate(**valid_data)
    assert user.name == "João Silva"
    assert user.email == "joao@exemplo.com" # Normalização para lowercase
    
    # Erro: nome muito curto
    with pytest.raises(ValidationError):
        UserCreate(**{**valid_data, "name": "a"})
        
    # Erro: nome muito longo
    with pytest.raises(ValidationError):
        UserCreate(**{**valid_data, "name": "a" * 101})
        
    # Erro: email inválido
    with pytest.raises(ValidationError):
        UserCreate(**{**valid_data, "email": "invalid-email"})
        
    # Erro: telefone sem prefixo +55
    with pytest.raises(ValidationError):
        UserCreate(**{**valid_data, "phone": "11999999999"})
        
    # Erro: telefone com letras
    with pytest.raises(ValidationError):
        UserCreate(**{**valid_data, "phone": "+551199999ABCD"})
        
    # Erro: senha curta
    with pytest.raises(ValidationError):
        UserCreate(**{**valid_data, "password": "short"})
        
    # Erro: consentimento termos False
    with pytest.raises(ValidationError) as exc:
        UserCreate(**{**valid_data, "consent_terms": False})
    assert "Aceite obrigatório dos termos" in str(exc.value)
    
    # Erro: consentimento privacidade ausente
    data_no_privacy = valid_data.copy()
    del data_no_privacy["consent_privacy"]
    with pytest.raises(ValidationError):
        UserCreate(**data_no_privacy)

def test_professional_create_schema_validation():
    """Testa validações do schema ProfessionalCreate."""
    valid_data = {
        "bio": "Profissional experiente em reformas.",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "service_radius_km": 50,
        "hourly_rate_cents": 5000,
        "category_ids": [str(uuid4()), str(uuid4())],
        "document_type": "cpf"
    }
    prof = ProfessionalCreate(**valid_data)
    assert prof.document_type == "cpf"
    
    # Erro: latitude fora de range
    with pytest.raises(ValidationError):
        ProfessionalCreate(**{**valid_data, "latitude": 91})
        
    # Erro: longitude fora de range
    with pytest.raises(ValidationError):
        ProfessionalCreate(**{**valid_data, "longitude": 181})
        
    # Erro: raio zero
    with pytest.raises(ValidationError):
        ProfessionalCreate(**{**valid_data, "service_radius_km": 0})
        
    # Erro: raio excessivo
    with pytest.raises(ValidationError):
        ProfessionalCreate(**{**valid_data, "service_radius_km": 201})
        
    # Erro: valor hora zero/negativo
    with pytest.raises(ValidationError):
        ProfessionalCreate(**{**valid_data, "hourly_rate_cents": 0})
    with pytest.raises(ValidationError):
        ProfessionalCreate(**{**valid_data, "hourly_rate_cents": -1})
        
    # Erro: categorias vazias ou excessivas
    with pytest.raises(ValidationError):
        ProfessionalCreate(**{**valid_data, "category_ids": []})
    with pytest.raises(ValidationError):
        ProfessionalCreate(**{**valid_data, "category_ids": [str(uuid4()) for _ in range(11)]})
        
    # Erro: tipo de documento inválido
    with pytest.raises(ValidationError):
        ProfessionalCreate(**{**valid_data, "document_type": "passaporte"})
        
    # Erro: bio muito longa
    with pytest.raises(ValidationError):
        ProfessionalCreate(**{**valid_data, "bio": "a" * 1001})

def test_login_refresh_delete_schemas():
    """Testa schemas de Login, Refresh e Delete Account."""
    # Login
    with pytest.raises(ValidationError):
        LoginRequest(email="invalid", password="123")
    with pytest.raises(ValidationError):
        LoginRequest(email="test@test.com", password="")
        
    # Refresh
    with pytest.raises(ValidationError):
        RefreshRequest(refresh_token="")
        
    # Delete
    with pytest.raises(ValidationError):
        DeleteAccountRequest(password="")

def test_lgpd_consent_payload_schema():
    """Testa schema ConsentPayload da LGPD."""
    valid_data = {"consent_terms": True, "consent_privacy": True}
    ConsentPayload(**valid_data)
    
    with pytest.raises(ValidationError):
        ConsentPayload(consent_terms=False, consent_privacy=True)
    with pytest.raises(ValidationError):
        ConsentPayload(consent_terms=True, consent_privacy=False)
    with pytest.raises(ValidationError):
        ConsentPayload(consent_terms=True) # Faltando privacidade
