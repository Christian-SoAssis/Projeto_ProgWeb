import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """O endpoint /health deve retornar status ok."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data


@pytest.mark.asyncio
async def test_api_v1_root(client: AsyncClient):
    """O endpoint /api/v1 deve responder."""
    response = await client.get("/api/v1/")
    assert response.status_code == 200
