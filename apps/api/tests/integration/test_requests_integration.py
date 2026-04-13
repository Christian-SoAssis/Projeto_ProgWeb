import pytest
import pytest_asyncio
import uuid
import io
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from sqlalchemy import select
from app.models.request import Request, RequestImage
from app.models.category import Category
from app.models.user import User

@pytest_asyncio.fixture(scope="function")
async def auth_client(client, db_session):
    """Cria um usuário cliente e retorna o client com headers de autenticação."""
    from app.core.security import create_access_token
    
    user = User(
        email=f"client_{uuid.uuid4().hex[:6]}@example.com",
        name="Test Client",
        password_hash="fakehash-$2b$12$6/9q...", # Mock hash
        role="client",
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    
    access_token = create_access_token(data={"sub": str(user.id)})
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    return client, user

@pytest_asyncio.fixture(scope="function")
async def sample_category(db_session):
    # Seed de uma categoria para o teste de criação
    cat = Category(
        name="Limpeza",
        slug="limpeza",
        color="#FFFFFF",
        sort_order=0
    )
    db_session.add(cat)
    await db_session.flush()
    await db_session.refresh(cat)
    return cat

@pytest_asyncio.fixture(autouse=True)
async def mock_vlm_enqueue():
    """Mocka a função de enqueue do ARQ para evitar conexão com Redis real."""
    with patch("app.services.request_service.create_pool", new_callable=AsyncMock) as mock_pool:
        mock_redis = AsyncMock()
        mock_pool.return_value = mock_redis
        yield mock_redis

@pytest.mark.asyncio
async def test_create_request_success(auth_client, sample_category):
    client, user = auth_client
    
    data = {
        "title": "Limpeza de Sofá",
        "description": "Sofá de 3 lugares retrátil",
        "category_id": str(sample_category.id),
        "urgency": "scheduled",
        "latitude": -23.55,
        "longitude": -46.63,
        "budget_cents": 25000
    }
    
    response = await client.post("/api/v1/requests", data=data)
    
    assert response.status_code == 201
    res_json = response.json()
    assert res_json["title"] == "Limpeza de Sofá"
    assert res_json["status"] == "open"

@pytest.mark.asyncio
async def test_create_request_with_images(auth_client, sample_category):
    client, user = auth_client
    
    data = {
        "title": "Reparo de Pia",
        "category_id": str(sample_category.id),
        "urgency": "immediate",
        "latitude": -23.55,
        "longitude": -46.63
    }
    
    # Simular arquivos Multipart
    files = [
        ("images", ("test1.jpg", io.BytesIO(b"fake_image_content"), "image/jpeg")),
        ("images", ("test2.png", io.BytesIO(b"fake_image_content"), "image/png"))
    ]
    
    response = await client.post("/api/v1/requests", data=data, files=files)
    
    assert response.status_code == 201
    res_json = response.json()
    assert len(res_json["images"]) == 2
    assert res_json["images"][0]["analyzed"] is False

@pytest.mark.asyncio
async def test_create_request_errors(auth_client, sample_category):
    client, user = auth_client
    
    # Campo obrigatório ausente (title)
    response = await client.post("/api/v1/requests", data={"category_id": str(sample_category.id)})
    assert response.status_code == 422
    
    # Latitude inválida
    data = {
        "title": "Erro Geo",
        "category_id": str(sample_category.id),
        "urgency": "immediate",
        "latitude": 91, # Invalido
        "longitude": 0
    }
    response = await client.post("/api/v1/requests", data=data)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_list_requests_ownership(auth_client, sample_category, db_session):
    client, user = auth_client
    
    # Criar um pedido para o usuário atual
    req = Request(
        client_id=user.id,
        category_id=sample_category.id,
        title="Meu Pedido",
        urgency="flexible",
        location="POINT(0 0)",
        status="open"
    )
    db_session.add(req)
    
    # Criar um pedido de OUTRO usuário
    other_user = User(email=f"other_{uuid.uuid4().hex[:6]}@test.com", name="Other", password_hash="...", role="client")
    db_session.add(other_user)
    await db_session.flush()
    
    req_other = Request(
        client_id=other_user.id,
        category_id=sample_category.id,
        title="Outro Pedido",
        urgency="flexible",
        location="POINT(0 0)",
        status="open"
    )
    db_session.add(req_other)
    await db_session.flush()
    
    # Listar apenas pedidos do cliente (client_only=True)
    response = await client.get("/api/v1/requests", params={"client_only": "true"})
    assert response.status_code == 200
    res_json = response.json()
    assert len(res_json) == 1
    assert res_json[0]["title"] == "Meu Pedido"

@pytest.mark.asyncio
async def test_pagination(auth_client, sample_category, db_session):
    client, user = auth_client
    
    # Criar 5 pedidos
    for i in range(5):
        req = Request(
            client_id=user.id, 
            category_id=sample_category.id, 
            title=f"Pedido {i}", 
            urgency="flexible", 
            location="POINT(0 0)",
            status="open"
        )
        db_session.add(req)
    await db_session.flush()
    
    # Testar limite 2
    response = await client.get("/api/v1/requests", params={"limit": 2, "offset": 0})
    assert response.status_code == 200
    assert len(response.json()) == 2
