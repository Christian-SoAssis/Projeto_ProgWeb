import hmac
import hashlib
import httpx
import logging
import uuid
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class MercadoPagoService:
    def __init__(self):
        self.access_token = settings.MERCADOPAGO_ACCESS_TOKEN
        self.webhook_secret = settings.MERCADOPAGO_WEBHOOK_SECRET
        self.base_url = "https://api.mercadopago.com"

    async def create_preference(
        self, 
        title: str, 
        amount_cents: int, 
        fee_cents: int, 
        external_reference: str,
        notification_url: str
    ) -> Optional[Dict[str, Any]]:
        if not self.access_token or "mock" in self.access_token or settings.ENVIRONMENT == "development":
            logger.info(f"[MOCK] Criando preferência de pagamento no MercadoPago para {external_reference}")
            return {
                "id": f"pref_{uuid.uuid4().hex[:10]}",
                "init_point": "https://www.mercadopago.com.br/sandbox/button"
            }

        url = f"{self.base_url}/checkout/preferences"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Converter centavos para float (MercadoPago usa decimais)
        unit_price = amount_cents / 100.0
        marketplace_fee = fee_cents / 100.0
        
        payload = {
            "items": [
                {
                    "title": title,
                    "quantity": 1,
                    "unit_price": unit_price,
                    "currency_id": "BRL"
                }
            ],
            "marketplace_fee": marketplace_fee,
            "external_reference": external_reference,
            "notification_url": notification_url,
            "back_urls": {
                "success": f"{settings.FRONTEND_AUTH_CALLBACK_URL}/payment/success",
                "failure": f"{settings.FRONTEND_AUTH_CALLBACK_URL}/payment/failure",
                "pending": f"{settings.FRONTEND_AUTH_CALLBACK_URL}/payment/pending"
            },
            "auto_return": "approved"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Erro ao criar preferência no MercadoPago: {str(e)}")
            return None

    def verify_webhook_signature(self, x_signature: str, x_request_id: str, payload_body: str) -> bool:
        """
        Valida a assinatura HMAC-SHA256 do webhook do MercadoPago.
        """
        if not x_signature:
            if settings.ENVIRONMENT == "production":
                logger.warning("Tentativa de webhook sem assinatura em produção.")
                return False
            return True

        if not self.webhook_secret:
            logger.warning("Secret do webhook não configurado.")
            return False
            
        try:
            # Parse parts: e.g. "ts=1672531199,v1=abc..." or "v1=abc,ts=1672531199"
            parts = {}
            for item in x_signature.split(','):
                if '=' in item:
                    k, v = item.split('=', 1)
                    parts[k.strip()] = v.strip()
            
            timestamp = parts.get('ts')
            received_hash = parts.get('v1')

            if not timestamp or not received_hash:
                return False

            # O formato oficial do MercadoPago para a string a ser assinada:
            # f"id:{x_request_id};ts:{timestamp};"
            data_to_sign = f"id:{x_request_id or ''};ts:{timestamp};"
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                data_to_sign.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            if hmac.compare_digest(expected_signature, received_hash):
                return True
                
            return False
        except Exception as e:
            logger.error(f"Falha ao validar assinatura do webhook: {str(e)}")
            return False

    async def get_payment_details(self, payment_id: str) -> Optional[Dict[str, Any]]:
        if not self.access_token or "mock" in self.access_token or settings.ENVIRONMENT == "development":
            logger.info(f"[MOCK] Buscando detalhes de pagamento no MercadoPago para {payment_id}")
            return {
                "id": payment_id,
                "status": "approved",
                "external_reference": payment_id
            }

        url = f"{self.base_url}/v1/payments/{payment_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Erro ao buscar pagamento {payment_id}: {str(e)}")
            return None

    async def refund_payment(self, payment_id: str, amount_cents: int) -> bool:
        """
        Simula o estorno de um pagamento no MercadoPago.
        """
        url = f"{self.base_url}/v1/payments/{payment_id}/refunds"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        if "mock" in self.access_token or settings.ENVIRONMENT == "development":
            logger.info(f"[MOCK] Reembolso de {amount_cents} centavos solicitado para o pagamento {payment_id}")
            return True
            
        try:
            payload = {"amount": amount_cents / 100.0}
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Erro ao estornar pagamento no MercadoPago: {str(e)}")
            return False

mercado_pago_service = MercadoPagoService()
