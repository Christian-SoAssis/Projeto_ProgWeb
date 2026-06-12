import pytest
from uuid import uuid4
from datetime import datetime, timezone

from app.models.user import User, UserRole
from app.models.professional import Professional
from app.models.category import Category
from app.models.request import Request as RequestModel
from app.models.matching_event import MatchingEvent
from app.models.bid import Bid
from app.models.contract import Contract
from app.services.matching_service import get_matches
from app.matching.engine import matching_engine
from app.application.use_cases.update_bid_use_case import UpdateBidUseCase, UpdateBidInput
from app.infrastructure.database.repositories.bid_repository_impl import BidRepositoryImpl
from app.infrastructure.database.repositories.contract_repository_impl import ContractRepositoryImpl
from app.infrastructure.database.repositories.request_repository_impl import RequestRepositoryImpl
from sqlalchemy import select


async def setup_matching_fixtures(db_session):
    # 1. Category
    category = Category(
        name=f"Category_{uuid4().hex[:6]}",
        slug=f"cat-slug-{uuid4().hex[:6]}",
        color="#123456",
        sort_order=0
    )
    db_session.add(category)
    await db_session.flush()

    # 2. Client User
    client_user = User(
        email=f"client_{uuid4().hex[:6]}@test.com",
        name="Client User", password_hash="hash",
        role=UserRole.CLIENT, is_active=True
    )
    db_session.add(client_user)
    await db_session.flush()

    # 3. Request
    request_model = RequestModel(
        id=uuid4(),
        client_id=client_user.id,
        category_id=category.id,
        title="Matching Test Request",
        description="Testing matching logic",
        location=f"POINT(-40.0 -20.0)",
        urgency="scheduled",
        budget_cents=10000,
        status="open",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(request_model)
    await db_session.flush()

    # 4. Professionals (2 professionals in range with different ratings)
    prof1_user = User(
        email=f"prof1_{uuid4().hex[:6]}@test.com",
        name="Professional One", password_hash="hash",
        role=UserRole.PROFESSIONAL, is_active=True
    )
    db_session.add(prof1_user)
    await db_session.flush()
    
    prof1 = Professional(
        user_id=prof1_user.id, bio="Professional 1 bio",
        latitude=-20.0, longitude=-40.0, service_radius_km=10.0,
        hourly_rate_cents=5000, is_verified=True, reputation_score=4.0
    )
    prof1.categories.append(category)
    db_session.add(prof1)

    prof2_user = User(
        email=f"prof2_{uuid4().hex[:6]}@test.com",
        name="Professional Two", password_hash="hash",
        role=UserRole.PROFESSIONAL, is_active=True
    )
    db_session.add(prof2_user)
    await db_session.flush()
    
    prof2 = Professional(
        user_id=prof2_user.id, bio="Professional 2 bio",
        latitude=-20.0, longitude=-40.0, service_radius_km=10.0,
        hourly_rate_cents=6000, is_verified=True, reputation_score=4.8
    )
    prof2.categories.append(category)
    db_session.add(prof2)
    await db_session.flush()

    return request_model, prof1, prof2


def mock_contract_count(db_session, count_val=500):
    original_execute = db_session.execute
    
    async def mock_execute(statement, *args, **kwargs):
        stmt_str = str(statement)
        if "count" in stmt_str and "contracts" in stmt_str:
            class MockResult:
                def scalar(self):
                    return count_val
                def scalars(self):
                    return self
                def all(self):
                    return [count_val]
            return MockResult()
        return await original_execute(statement, *args, **kwargs)
        
    db_session.execute = mock_execute
    return original_execute


@pytest.mark.asyncio
async def test_cold_start_matching(db_session):
    request_model, prof1, prof2 = await setup_matching_fixtures(db_session)

    # No completed contracts exist yet (< 500)
    mock_contract_count(db_session, 100)
    matching_engine.mock_mode = True
    
    class MockTaskQueue:
        def __init__(self):
            self.jobs = []
        async def enqueue(self, task_name, *args, **kwargs):
            self.jobs.append((task_name, args, kwargs))

    queue = MockTaskQueue()
    matches = await get_matches(db_session, request_model, task_queue=queue)
    
    # Under rules-based V0, candidates should be sorted by reputation_score DESC
    assert len(matches) == 2
    assert matches[0]["id"] == prof2.id
    assert matches[1]["id"] == prof1.id
    
    # Impression events should be enqueued
    assert len(queue.jobs) == 1
    assert queue.jobs[0][0] == "log_matching_event_task"
    events = queue.jobs[0][1][0]
    assert len(events) == 2
    assert events[0]["event_type"] == "impression"
    assert events[0]["professional_id"] == str(prof2.id)
    assert events[1]["professional_id"] == str(prof1.id)


@pytest.mark.asyncio
async def test_ltr_matching_activated(db_session):
    request_model, prof1, prof2 = await setup_matching_fixtures(db_session)

    # Mock 500 completed contracts count
    mock_contract_count(db_session, 500)

    # Enable mock LTR matching
    matching_engine.mock_mode = True
    
    class MockTaskQueue:
        def __init__(self):
            self.jobs = []
        async def enqueue(self, task_name, *args, **kwargs):
            self.jobs.append((task_name, args, kwargs))

    # Override score to return higher score for prof1 (index 1 in V0)
    original_score = matching_engine.score
    matching_engine.score = lambda features: [1.0, 5.0]
    
    queue = MockTaskQueue()
    matches = await get_matches(db_session, request_model, task_queue=queue)
    
    # Sorted by matching_score DESC, so prof1 first
    assert len(matches) == 2
    assert matches[0]["id"] == prof1.id
    assert matches[1]["id"] == prof2.id
    
    # Restore original score method
    matching_engine.score = original_score


@pytest.mark.asyncio
async def test_ltr_matching_fallback_on_error(db_session):
    request_model, prof1, prof2 = await setup_matching_fixtures(db_session)

    # Mock 500 completed contracts count
    mock_contract_count(db_session, 500)

    matching_engine.mock_mode = True
    original_score = matching_engine.score
    
    def raise_error(features):
        raise RuntimeError("LightGBM prediction failed internally")
    matching_engine.score = raise_error

    class MockTaskQueue:
        def __init__(self):
            self.jobs = []
        async def enqueue(self, task_name, *args, **kwargs):
            self.jobs.append((task_name, args, kwargs))

    queue = MockTaskQueue()
    matches = await get_matches(db_session, request_model, task_queue=queue)
    
    # Fallback to rules-based sorting (V0) -> prof2 (4.8) first
    assert len(matches) == 2
    assert matches[0]["id"] == prof2.id
    assert matches[1]["id"] == prof1.id
    
    # Restore original score method
    matching_engine.score = original_score


@pytest.mark.asyncio
async def test_conversion_logging_on_bid_acceptance(db_session):
    request_model, prof1, prof2 = await setup_matching_fixtures(db_session)

    # Create a pending bid
    bid = Bid(
        id=uuid4(),
        request_id=request_model.id,
        professional_id=prof1.id,
        price_cents=5000,
        estimated_hours=4,
        status="pending"
    )
    db_session.add(bid)
    await db_session.flush()

    class MockTaskQueue:
        def __init__(self):
            self.jobs = []
        async def enqueue(self, task_name, *args, **kwargs):
            self.jobs.append((task_name, args, kwargs))

    queue = MockTaskQueue()
    
    bid_repo = BidRepositoryImpl(db_session)
    contract_repo = ContractRepositoryImpl(db_session)
    request_repo = RequestRepositoryImpl(db_session)
    
    use_case = UpdateBidUseCase(bid_repo, contract_repo, request_repo, task_queue=queue)
    
    input_data = UpdateBidInput(
        bid_id=bid.id,
        client_user_id=request_model.client_id,
        new_status="accepted",
        scheduled_start=datetime.now(timezone.utc)
    )
    
    updated_bid, contract = await use_case.execute(input_data)
    await db_session.flush()

    assert contract is not None
    assert updated_bid.status == "accepted"
    
    # Conversion event enqueued
    assert len(queue.jobs) == 1
    assert queue.jobs[0][0] == "log_matching_event_task"
    events = queue.jobs[0][1][0]
    assert len(events) == 1
    assert events[0]["event_type"] == "conversion"
    assert events[0]["request_id"] == str(request_model.id)
    assert events[0]["professional_id"] == str(prof1.id)
    assert events[0]["bid_id"] == str(bid.id)


@pytest.mark.asyncio
async def test_log_matching_event_task_persists_to_db(db_session):
    request_model, prof1, prof2 = await setup_matching_fixtures(db_session)
    
    from app.core.worker import log_matching_event_task
    import app.core.worker
    
    # Mock session context manager to share the test transaction
    class MockSessionContext:
        def __init__(self, session):
            self.session = session
        async def __aenter__(self):
            return self.session
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
            
    original_maker = app.core.worker.async_session_maker
    app.core.worker.async_session_maker = lambda: MockSessionContext(db_session)
    
    try:
        evt_id = uuid4()
        event_data = {
            "id": str(evt_id),
            "event_type": "impression",
            "request_id": str(request_model.id),
            "professional_id": str(prof1.id),
            "bid_id": None,
            "position": 1,
            "features": {"distance_km": 2.5}
        }
        
        res = await log_matching_event_task({}, [event_data])
        assert "eventos persistidos" in res
        await db_session.flush()
        
        # Verify database persistence
        stmt = select(MatchingEvent).where(MatchingEvent.id == evt_id)
        db_res = await db_session.execute(stmt)
        persisted_event = db_res.scalar_one_or_none()
        
        assert persisted_event is not None
        assert persisted_event.event_type == "impression"
        assert persisted_event.request_id == request_model.id
        assert persisted_event.professional_id == prof1.id
        assert persisted_event.position == 1
        assert persisted_event.features == {"distance_km": 2.5}
    finally:
        app.core.worker.async_session_maker = original_maker
