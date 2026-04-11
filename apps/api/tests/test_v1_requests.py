import pytest
from httpx import AsyncClient
import uuid
from unittest.mock import AsyncMock, patch
from app.models.category import Category
from app.core.config import settings

@pytest.fixture
async def sample_category(db_session):
    cat = Category(
        id=uuid.uuid4(),
        name="Hidráulica",
        slug="hidraulica",
        color="#2e7bc4"
    )
    db_session.add(cat)
    await db_session.commit()
    return cat

@pytest.mark.asyncio
async def test_create_request_success(
    client: AsyncClient, 
    auth_headers: dict, 
    sample_category: Category
):
    """
    Testa a criação de um pedido com uma imagem.
    Mocks: VLMService (IA) e ARQ pool.
    """
    # Mock do ARQ para não tentar conectar ao Redis real durante o teste unitário de endpoint
    with patch("app.services.request_service.create_pool") as mock_pool:
        mock_redis = AsyncMock()
        mock_pool.return_value = mock_redis
        
        # Dados do form
        data = {
            "title": "Vazamento na pia da cozinha",
            "description": "Tem um cano estourado embaixo da pia",
            "category_id": str(sample_category.id),
            "urgency": "immediate",
            "latitude": -23.5505,
            "longitude": -46.6333,
            "budget_cents": 15000
        }
        
        # Arquivo fake
        files = {
            "images": ("test.jpg", b"fake-image-content", "image/jpeg")
        }
        
        response = await client.post(
            "/api/v1/requests",
            data=data,
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        res_data = response.json()
        assert res_data["title"] == data["title"]
        assert len(res_data["images"]) == 1
        assert res_data["status"] == "open"
        
        # Verificar se o job de análise foi enfileirado
        mock_redis.enqueue_job.assert_called_once()

@pytest.mark.asyncio
async def test_list_requests(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/requests", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_request_not_found(client: AsyncClient, auth_headers: dict):
    fake_id = uuid.uuid4()
    response = await client.get(f"/api/v1/requests/{fake_id}", headers=auth_headers)
    assert response.status_code == 404
