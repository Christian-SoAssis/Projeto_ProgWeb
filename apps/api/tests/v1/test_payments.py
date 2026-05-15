import pytest
import uuid
from unittest.mock import AsyncMock, patch
from fastapi import status
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_payment_intent_not_found(client: AsyncClient, auth_headers: dict):
    """Testa erro 404 quando o contrato não existe."""
    response = await client.post(
        f"/api/v1/payments/{uuid.uuid4()}/intent",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_webhook_payment_success(client: AsyncClient):
    """Testa o processamento básico do webhook (mockado)."""
    payload = {
        "action": "payment.created",
        "api_version": "v1",
        "data": {"id": "12345"},
        "date_created": "2026-05-15T13:00:00Z",
        "id": "67890",
        "live_mode": False,
        "type": "payment",
        "user_id": "1"
    }
    
    with patch("app.services.payment_service.handle_payment_webhook", new_callable=AsyncMock) as mock_handle:
        response = await client.post("/api/v1/payments/webhook", json=payload)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}
        mock_handle.assert_called_once()

@pytest.mark.asyncio
async def test_open_dispute_validation(client: AsyncClient, auth_headers: dict):
    """Testa validação de campos ao abrir disputa."""
    payload = {
        "payment_id": str(uuid.uuid4()),
        "reason": "Curto", # Menor que 10 chars
        "category": "invalid"
    }
    response = await client.post(
        "/api/v1/payments/disputes",
        json=payload,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
