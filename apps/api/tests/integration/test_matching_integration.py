import pytest
import pytest_asyncio
import uuid
from uuid import uuid4
from sqlalchemy import text
from geoalchemy2 import WKTElement
from app.models.user import User, UserRole
from app.models.request import Request
from app.models.category import Category
from app.models.professional import Professional
from app.core.security import create_access_token

@pytest_asyncio.fixture
async def matching_setup(db_session, client):
    """Cria request + profissionais para testar matching."""
    
    # 1. Criar cliente com request aberto
    client_user = User(
        email=f"client_{uuid4().hex[:6]}@test.com",
        name="Test Client",
        password_hash="fakehash",
        role=UserRole.CLIENT,
        is_active=True
    )
    db_session.add(client_user)
    
    # 2. Criar categoria
    category = Category(
        name="Hidráulica", 
        slug=f"hidraulica_{uuid4().hex[:4]}", 
        color="#0000FF",
        is_active=True
    )
    db_session.add(category)
    await db_session.flush()
    
    # 3. Criar request do cliente
    request = Request(
        client_id=client_user.id,
        category_id=category.id,
        title="Torneira vazando",
        urgency="immediate",
        location=WKTElement("POINT(-45.42 -21.55)", srid=4326),  # Varginha-MG
        status="open"
    )
    db_session.add(request)
    await db_session.flush()
    
    # 4. Criar 3 profissionais verificados na mesma categoria
    professionals = []
    for i in range(3):
        prof_user = User(
            email=f"prof_{uuid4().hex[:6]}@test.com",
            name=f"Prof {i}", 
            password_hash="hash",
            role=UserRole.PROFESSIONAL,
            is_active=True
        )
        db_session.add(prof_user)
        await db_session.flush()
        
        prof = Professional(
            user_id=prof_user.id,
            bio="Profissional experiente",
            latitude=-21.55 + (i * 0.01),   # próximos a Varginha
            longitude=-45.42 + (i * 0.01),
            service_radius_km=30.0,
            hourly_rate_cents=5000,
            reputation_score=4.0 - (i * 0.5),
            is_verified=True
        )
        db_session.add(prof)
        await db_session.flush()
        
        # Associar à categoria
        await db_session.execute(
            text("INSERT INTO professional_categories (professional_id, category_id) VALUES (:pid, :cid)"),
            {"pid": prof.id, "cid": category.id}
        )
        professionals.append(prof)
    
    # 5. Criar 1 profissional NÃO verificado (não deve aparecer)
    unverified_user = User(
        email=f"unverified_{uuid4().hex[:6]}@test.com",
        name="Unverified", 
        password_hash="hash",
        role=UserRole.PROFESSIONAL,
        is_active=True
    )
    db_session.add(unverified_user)
    await db_session.flush()
    unverified = Professional(
        user_id=unverified_user.id,
        bio="Não verificado",
        latitude=-21.55, 
        longitude=-45.42,
        service_radius_km=30.0,
        hourly_rate_cents=3000,
        reputation_score=5.0,
        is_verified=False
    )
    db_session.add(unverified)
    await db_session.flush()
    await db_session.execute(
        text("INSERT INTO professional_categories (professional_id, category_id) VALUES (:pid, :cid)"),
        {"pid": unverified.id, "cid": category.id}
    )
    
    await db_session.flush()
    await db_session.commit()
    
    token = create_access_token(data={"sub": str(client_user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    
    return {
        "client": client_user,
        "request": request,
        "category": category,
        "professionals": professionals,
        "headers": headers
    }

@pytest.mark.asyncio
async def test_matches_returns_verified_only(client, matching_setup):
    """Apenas profissionais verificados aparecem."""
    resp = await client.get(
        f"/api/v1/requests/{matching_setup['request'].id}/matches",
        headers=matching_setup["headers"]
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3  # 3 verificados, não o unverified
    for match in data:
        assert match["is_verified"] is True

@pytest.mark.asyncio
async def test_matches_ordered_by_reputation(client, matching_setup):
    """Resultados ordenados por reputation_score DESC."""
    resp = await client.get(
        f"/api/v1/requests/{matching_setup['request'].id}/matches",
        headers=matching_setup["headers"]
    )
    assert resp.status_code == 200
    data = resp.json()
    scores = [m["reputation_score"] for m in data]
    assert scores == sorted(scores, reverse=True)

@pytest.mark.asyncio
async def test_matches_includes_distance(client, matching_setup):
    """Cada resultado inclui distance_km."""
    resp = await client.get(
        f"/api/v1/requests/{matching_setup['request'].id}/matches",
        headers=matching_setup["headers"]
    )
    assert resp.status_code == 200
    data = resp.json()
    for match in data:
        assert "distance_km" in match
        assert match["distance_km"] >= 0

@pytest.mark.asyncio
async def test_matches_request_not_found(client, matching_setup):
    resp = await client.get(
        f"/api/v1/requests/{uuid4()}/matches",
        headers=matching_setup["headers"]
    )
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_matches_forbidden_other_client(client, matching_setup, db_session):
    """Cliente diferente não pode ver matches de outro cliente."""
    other = User(
        email=f"other_{uuid4().hex[:6]}@test.com", 
        name="Other",
        password_hash="hash", 
        role=UserRole.CLIENT,
        is_active=True
    )
    db_session.add(other)
    await db_session.flush()
    await db_session.commit()

    token = create_access_token(data={"sub": str(other.id)})
    resp = await client.get(
        f"/api/v1/requests/{matching_setup['request'].id}/matches",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_matches_unauthenticated(client, matching_setup):
    resp = await client.get(
        f"/api/v1/requests/{matching_setup['request'].id}/matches"
    )
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_matches_empty_when_no_professionals(client, db_session):
    """Request sem profissionais compatíveis retorna lista vazia."""
    # Criar request numa categoria sem profissionais
    client_user = User(
        email=f"lonely_{uuid4().hex[:6]}@test.com", 
        name="Lonely",
        password_hash="hash", 
        role=UserRole.CLIENT,
        is_active=True
    )
    db_session.add(client_user)
    cat = Category(
        name="Sem prof", 
        slug=f"noprof_{uuid4().hex[:4]}", 
        color="#000000",
        is_active=True
    )
    db_session.add(cat)
    await db_session.flush()
    req = Request(
        client_id=client_user.id,
        category_id=cat.id,
        title="Pedido sem match",
        urgency="flexible",
        location=WKTElement("POINT(-45.42 -21.55)", srid=4326),
        status="open"
    )
    db_session.add(req)
    await db_session.flush()
    await db_session.commit()

    token = create_access_token(data={"sub": str(client_user.id)})
    resp = await client.get(
        f"/api/v1/requests/{req.id}/matches",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json() == []
