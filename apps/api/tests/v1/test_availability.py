import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, time, timezone, date, timedelta
from pydantic import ValidationError

from app.schemas.v1.availability import ProfessionalPixKeyCreate
from app.models.user import User, UserRole
from app.models.professional import Professional
from app.models.professional_pix_key import ProfessionalPixKey
from app.models.professional_availability import ProfessionalAvailability
from app.models.contract import Contract
from app.models.category import Category
from app.models.request import Request as RequestModel
from app.core.security import create_access_token

# --- 1. Schema Validations ---

def test_pix_key_schema_cpf():
    # Clean CPF
    key = ProfessionalPixKeyCreate(key_type="cpf", key_value="123.456.789-00")
    assert key.key_value == "12345678900"

    with pytest.raises(ValidationError):
         ProfessionalPixKeyCreate(key_type="cpf", key_value="123")


def test_pix_key_schema_cnpj():
    # Clean CNPJ
    key = ProfessionalPixKeyCreate(key_type="cnpj", key_value="12.345.678/0001-90")
    assert key.key_value == "12345678000190"

    with pytest.raises(ValidationError):
         ProfessionalPixKeyCreate(key_type="cnpj", key_value="123")


def test_pix_key_schema_phone():
    # Prepend 55 and clean non-digits
    key1 = ProfessionalPixKeyCreate(key_type="phone", key_value="11999998888")
    assert key1.key_value == "+5511999998888"

    key2 = ProfessionalPixKeyCreate(key_type="phone", key_value="+55 (11) 99999-8888")
    assert key2.key_value == "+5511999998888"

    with pytest.raises(ValidationError):
         ProfessionalPixKeyCreate(key_type="phone", key_value="123")


def test_pix_key_schema_random():
    # Valid UUID
    val_uuid = str(uuid4())
    key = ProfessionalPixKeyCreate(key_type="random", key_value=val_uuid)
    assert key.key_value == val_uuid.lower()

    with pytest.raises(ValidationError):
         ProfessionalPixKeyCreate(key_type="random", key_value="not-a-uuid")


# --- 2. Endpoint Tests ---

@pytest.mark.asyncio
async def test_professional_pix_endpoints(client, db_session):
    # 1. Setup professional user
    user = User(
        email=f"prof_{uuid4().hex[:6]}@test.com",
        name="Pix Professional", password_hash="hash",
        role=UserRole.PROFESSIONAL, is_active=True
    )
    db_session.add(user)
    await db_session.flush()

    prof = Professional(
        user_id=user.id, bio="Professional bio details",
        latitude=-20.0, longitude=-40.0, service_radius_km=10,
        hourly_rate_cents=5000, is_verified=True
    )
    db_session.add(prof)
    await db_session.flush()

    token = create_access_token(data={"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Save Pix key
    payload = {"key_type": "cpf", "key_value": "111.222.333-44"}
    resp_post = await client.post("/api/v1/auth/professional/pix", json=payload, headers=headers)
    assert resp_post.status_code == 200
    data_post = resp_post.json()
    assert data_post["key_type"] == "cpf"
    assert data_post["key_value"] == "***.***.333-44"  # LGPD Masked response

    # 3. Get Pix key
    resp_get = await client.get("/api/v1/auth/professional/pix", headers=headers)
    assert resp_get.status_code == 200
    data_get = resp_get.json()
    assert data_get["key_type"] == "cpf"
    assert data_get["key_value"] == "***.***.333-44"


@pytest.mark.asyncio
async def test_professional_availability_endpoints(client, db_session):
    # 1. Setup professional user
    user = User(
        email=f"prof_{uuid4().hex[:6]}@test.com",
        name="Avail Professional", password_hash="hash",
        role=UserRole.PROFESSIONAL, is_active=True
    )
    db_session.add(user)
    await db_session.flush()

    prof = Professional(
        user_id=user.id, bio="Professional bio details",
        latitude=-20.0, longitude=-40.0, service_radius_km=10,
        hourly_rate_cents=5000, is_verified=True
    )
    db_session.add(prof)
    await db_session.flush()

    token = create_access_token(data={"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Save weekly availability (e.g. Monday/Segunda, day_of_week=1, 09:00 - 17:00)
    payload = {
        "availabilities": [
            {
                "day_of_week": 1,
                "start_time": "09:00:00",
                "end_time": "17:00:00",
                "is_active": True
            }
        ]
    }
    resp_post = await client.post("/api/v1/auth/professional/availability", json=payload, headers=headers)
    assert resp_post.status_code == 200

    # 3. Get availability
    resp_get = await client.get("/api/v1/auth/professional/availability", headers=headers)
    assert resp_get.status_code == 200
    data_get = resp_get.json()
    assert len(data_get["availabilities"]) == 1
    assert data_get["availabilities"][0]["day_of_week"] == 1
    assert data_get["availabilities"][0]["start_time"] == "09:00:00"
    assert data_get["availabilities"][0]["end_time"] == "17:00:00"


# --- 3. Available Slots Calculation (with 1h travel buffer) ---

@pytest.mark.asyncio
async def test_available_slots_calculation(client, db_session):
    # 1. Setup client and professional
    client_user = User(
        email=f"client_{uuid4().hex[:6]}@test.com",
        name="Client for Slot", password_hash="hash",
        role=UserRole.CLIENT, is_active=True
    )
    db_session.add(client_user)

    prof_user = User(
        email=f"prof_{uuid4().hex[:6]}@test.com",
        name="Prof for Slot", password_hash="hash",
        role=UserRole.PROFESSIONAL, is_active=True
    )
    db_session.add(prof_user)
    await db_session.flush()

    prof = Professional(
        user_id=prof_user.id, bio="Professional bio details",
        latitude=-20.0, longitude=-40.0, service_radius_km=10,
        hourly_rate_cents=5000, is_verified=True
    )
    db_session.add(prof)
    await db_session.flush()

    # 2. Set availability for Monday (day_of_week = 1) between 09:00 and 14:00
    availability = ProfessionalAvailability(
        professional_id=prof.id,
        day_of_week=1,
        start_time=time(9, 0),
        end_time=time(14, 0),
        is_active=True
    )
    db_session.add(availability)
    await db_session.flush()

    # Query date: Monday, June 15, 2026
    query_date = date(2026, 6, 15)

    # 3. Retrieve available slots with no active contracts
    resp_empty = await client.get(f"/api/v1/professionals/{prof.id}/available-slots", params={"date": str(query_date)})
    assert resp_empty.status_code == 200
    slots_empty = resp_empty.json()
    # Expected slots of 1 hour: 09:00-10:00, 10:00-11:00, 11:00-12:00, 12:00-13:00, 13:00-14:00 (5 slots)
    assert len(slots_empty) == 5
    assert slots_empty[0]["start_time"] == "09:00"
    assert slots_empty[4]["start_time"] == "13:00"

    # 4. Insert an active contract on query_date from 11:00 to 12:00
    # Travel buffer is 1 hour before and after: conflict window = 10:00 to 13:00.
    # Therefore, slots starting at 10:00, 11:00, and 12:00 must be removed.
    # Available slots left: 09:00-10:00, 13:00-14:00.
    category = Category(
        name="Slots Category",
        slug=f"slots-cat-{uuid4().hex[:4]}",
        color="#FFFFFF",
        sort_order=0
    )
    db_session.add(category)
    await db_session.flush()

    request_model = RequestModel(
        id=uuid4(),
        client_id=client_user.id,
        category_id=category.id,
        title="Slot Testing Request",
        description="Testing available slots",
        location=f"POINT(-40.0 -20.0)",
        urgency="scheduled",
        budget_cents=10000,
        status="open",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(request_model)
    await db_session.flush()

    contract = Contract(
        request_id=request_model.id,
        professional_id=prof.id,
        client_id=client_user.id,
        agreed_cents=10000,
        status="active",
        scheduled_start=datetime.combine(query_date, time(11, 0)).replace(tzinfo=timezone.utc),
        scheduled_end=datetime.combine(query_date, time(12, 0)).replace(tzinfo=timezone.utc)
    )
    db_session.add(contract)
    await db_session.flush()

    resp_conflict = await client.get(f"/api/v1/professionals/{prof.id}/available-slots", params={"date": str(query_date)})
    assert resp_conflict.status_code == 200
    slots_conflict = resp_conflict.json()

    # Check remaining slots
    assert len(slots_conflict) == 2
    assert any(s["start_time"] == "09:00" for s in slots_conflict)
    assert any(s["start_time"] == "13:00" for s in slots_conflict)
    assert not any(s["start_time"] == "10:00" for s in slots_conflict)
    assert not any(s["start_time"] == "11:00" for s in slots_conflict)
    assert not any(s["start_time"] == "12:00" for s in slots_conflict)
