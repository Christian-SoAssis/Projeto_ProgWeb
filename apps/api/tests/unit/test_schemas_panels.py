import pytest
from uuid import uuid4
from pydantic import ValidationError
from app.schemas.v1.panels import NotificationMarkRead, FavoriteCreate

# NotificationMarkRead
def test_notification_mark_read_empty():
    # notification_ids=[] → ValidationError (min_length=1)
    with pytest.raises(ValidationError):
        NotificationMarkRead(notification_ids=[])

def test_notification_mark_read_too_many():
    # notification_ids com 101 UUIDs → ValidationError (max_length=100)
    with pytest.raises(ValidationError):
        NotificationMarkRead(notification_ids=[uuid4() for _ in range(101)])

def test_notification_mark_read_valid():
    # 1 UUID válido → OK
    obj = NotificationMarkRead(notification_ids=[uuid4()])
    assert len(obj.notification_ids) == 1

# FavoriteCreate
def test_favorite_create_invalid_uuid():
    # professional_id="not-uuid" → ValidationError
    with pytest.raises(ValidationError):
        FavoriteCreate(professional_id="not-uuid")

def test_favorite_create_valid():
    # UUID válido → OK
    uid = uuid4()
    obj = FavoriteCreate(professional_id=uid)
    assert obj.professional_id == uid
