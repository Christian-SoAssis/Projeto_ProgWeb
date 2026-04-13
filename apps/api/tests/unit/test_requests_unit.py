import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.vlm_service import VLMService, CATEGORIES
from app.core.utils import retry_with_backoff

# --------------------------------------------------------------------------
# 3.T1 — Testes Unitários: Validação de Geolocalização (Schemas Pydantic)
# Nota: Como a validação de geo está no Schema RequestCreate, 
# estes testes focam no comportamento esperado dos dados.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("lat,expected_valid", [
    (90, True),
    (-90, True),
    (90.1, False),
    (-90.1, False),
    (0, True),
])
def test_latitude_boundaries(lat, expected_valid):
    from app.schemas.v1.requests import RequestCreate
    from pydantic import ValidationError
    
    data = {
        "title": "Valid Title",
        "category_id": "550e8400-e29b-41d4-a716-446655440000",
        "urgency": "immediate",
        "latitude": lat,
        "longitude": 0
    }
    
    if expected_valid:
        obj = RequestCreate(**data)
        assert obj.latitude == lat
    else:
        with pytest.raises(ValidationError):
            RequestCreate(**data)

@pytest.mark.parametrize("lng,expected_valid", [
    (180, True),
    (-180, True),
    (180.1, False),
    (-180.1, False),
    (0, True),
])
def test_longitude_boundaries(lng, expected_valid):
    from app.schemas.v1.requests import RequestCreate
    from pydantic import ValidationError
    
    data = {
        "title": "Valid Title",
        "category_id": "550e8400-e29b-41d4-a716-446655440000",
        "urgency": "immediate",
        "latitude": 0,
        "longitude": lng
    }
    
    if expected_valid:
        obj = RequestCreate(**data)
        assert obj.longitude == lng
    else:
        with pytest.raises(ValidationError):
            RequestCreate(**data)

# --------------------------------------------------------------------------
# Validação de Urgência
# --------------------------------------------------------------------------

@pytest.mark.parametrize("urgency,expected_valid", [
    ("immediate", True),
    ("scheduled", True),
    ("flexible", True),
    ("urgent", False),
    ("high", False),
])
def test_urgency_values(urgency, expected_valid):
    from app.schemas.v1.requests import RequestCreate
    from pydantic import ValidationError
    
    data = {
        "title": "Valid Title",
        "category_id": "550e8400-e29b-41d4-a716-446655440000",
        "urgency": urgency,
        "latitude": 0,
        "longitude": 0
    }
    
    if expected_valid:
        obj = RequestCreate(**data)
        assert obj.urgency == urgency
    else:
        with pytest.raises(ValidationError):
            RequestCreate(**data)

# --------------------------------------------------------------------------
# Parsing de Output VLM
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_vlm_parsing_valid_json():
    service = VLMService()
    service.client = MagicMock()
    
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "category": "Hidráulica",
        "ai_complexity": "medium",
        "ai_urgency": "high",
        "ai_specialties": ["Vazamento", "Pia"]
    })
    service.client.models.generate_content.return_value = mock_response
    
    result = await service.analyze_images([b"fake_image"])
    
    assert result["category"] == "Hidráulica"
    assert result["ai_complexity"] == "medium"
    assert result["ai_urgency"] == "high"
    assert result["ai_specialties"] == ["Vazamento", "Pia"]

@pytest.mark.asyncio
async def test_vlm_parsing_missing_fields():
    service = VLMService()
    service.client = MagicMock()
    
    # JSON sem ai_complexity
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "category": "Elétrica",
        "ai_urgency": "low"
    })
    service.client.models.generate_content.return_value = mock_response
    
    result = await service.analyze_images([b"fake_image"])
    
    assert result["category"] == "Elétrica"
    assert result["ai_urgency"] == "low"
    assert "ai_complexity" not in result or result["ai_complexity"] is None # Depende do loads
    # No VLMService real, ele retorna o que json.loads retornar se não houver erro

@pytest.mark.asyncio
async def test_vlm_parsing_invalid_json_fallback():
    service = VLMService()
    service.client = MagicMock()
    
    mock_response = MagicMock()
    mock_response.text = "invalid json string"
    service.client.models.generate_content.return_value = mock_response
    
    result = await service.analyze_images([b"fake_image"])
    
    # Verifica se o fallback foi aplicado
    assert result["category"] is None
    assert result["ai_complexity"] == "medium"
    assert result["ai_urgency"] == "medium"
    assert result["ai_specialties"] == []

# --------------------------------------------------------------------------
# Lógica de Retry com Backoff Exponencial
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_retry_backoff_logic():
    mock_func = AsyncMock()
    # Simula 2 falhas e 1 sucesso
    mock_func.side_effect = [ValueError("Fail 1"), ValueError("Fail 2"), "Success"]
    
    # Decorador aplicado manualmente para o teste
    decorated_func = retry_with_backoff(
        retries=3, 
        initial_delay=0.01, 
        backoff_factor=2, 
        exceptions=(ValueError,)
    )(mock_func)
    
    result = await decorated_func()
    
    assert result == "Success"
    assert mock_func.call_count == 3

@pytest.mark.asyncio
async def test_retry_backoff_exhausted():
    mock_func = AsyncMock()
    mock_func.side_effect = ValueError("Always fails")
    
    decorated_func = retry_with_backoff(
        retries=2, 
        initial_delay=0.01, 
        backoff_factor=2, 
        exceptions=(ValueError,)
    )(mock_func)
    
    with pytest.raises(ValueError, match="Always fails"):
        await decorated_func()
    
    assert mock_func.call_count == 3 # Initial + 2 retries
