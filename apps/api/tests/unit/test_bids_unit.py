import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.services.bid_service import create_bid, update_bid
from app.models.professional import Professional
from app.models.request import Request
from app.models.bid import Bid

def mock_db_result(scalar=None, scalars=None):
    res = MagicMock()
    res.scalar_one_or_none.return_value = scalar
    if scalars is not None:
        res.scalars.return_value.all.return_value = scalars
    return res

@pytest.mark.asyncio
async def test_unverified_professional_cannot_bid():
    db = AsyncMock()
    prof = Professional(user_id=uuid.uuid4(), is_verified=False)
    
    # 1. Prof query
    db.execute.side_effect = [mock_db_result(scalar=prof)]
    
    with pytest.raises(HTTPException) as exc:
        await create_bid(db, prof.user_id, uuid.uuid4(), 1000)
    assert exc.value.status_code == 403

@pytest.mark.asyncio
async def test_bid_on_non_open_request():
    db = AsyncMock()
    prof = Professional(user_id=uuid.uuid4(), is_verified=True)
    req = Request(id=uuid.uuid4(), status="matched")
    
    # 1. Prof query, 2. Request query
    db.execute.side_effect = [
        mock_db_result(scalar=prof),
        mock_db_result(scalar=req)
    ]
    
    with pytest.raises(HTTPException) as exc:
        await create_bid(db, prof.user_id, req.id, 1000)
    assert exc.value.status_code == 409

@pytest.mark.asyncio
async def test_accept_bid_creates_contract_logic():
    db = AsyncMock()
    client_id = uuid.uuid4()
    req = Request(id=uuid.uuid4(), client_id=client_id, status="open")
    bid = Bid(id=uuid.uuid4(), request_id=req.id, price_cents=15000, status="pending")
    
    # 1. Bid query, 2. Request query, 3. Other bids query
    db.execute.side_effect = [
        mock_db_result(scalar=bid),
        mock_db_result(scalar=req),
        mock_db_result(scalars=[])
    ]
    
    updated_bid, contract = await update_bid(db, bid.id, client_id, "accepted")
    
    assert updated_bid.status == "accepted"
    assert contract.agreed_cents == 15000
    assert contract.status == "active"
    assert req.status == "matched"
