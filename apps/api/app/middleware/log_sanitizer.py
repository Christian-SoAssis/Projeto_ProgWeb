import re
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging

logger = logging.getLogger("uvicorn.error")

class LogSanitizerMiddleware(BaseHTTPMiddleware):
    """
    Middleware para mascarar informações sensíveis (PII) nos logs.
    Mascaramento aplicado: CPF, CNPJ e Tokens de Autorização.
    """
    
    # Regex para CPF: 000.000.000-00
    CPF_PATTERN = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
    # Regex para CNPJ: 00.000.000/0000-00
    CNPJ_PATTERN = re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b")
    # Regex para Authorization header
    AUTH_PATTERN = re.compile(r"Bearer\s+[\w\.-]+")

    def mask_text(self, text: str) -> str:
        """Aplica máscaras em um texto."""
        if not text:
            return text
            
        # Mascarar CPF (ex: ***.***.***-01)
        text = self.CPF_PATTERN.sub(lambda m: "***.***.***-" + m.group()[-2:], text)
        
        # Mascarar CNPJ (ex: **.***.****/****-90)
        text = self.CNPJ_PATTERN.sub(lambda m: "**.***.****/****-" + m.group()[-2:], text)
        
        # Mascarar Headers
        text = self.AUTH_PATTERN.sub("Bearer [REDACTED]", text)
        
        return text

    async def dispatch(self, request: Request, call_next):
        # 1. Obter informações básicas da request
        method = request.method
        url = str(request.url)
        client_host = request.client.host if request.client else "unknown"
        
        # 2. Registrar request (com headers mascarados)
        headers = dict(request.headers)
        if "authorization" in headers:
            headers["authorization"] = "Bearer [REDACTED]"
        
        logger.debug(f"Request: {method} {url} from {client_host} | Headers: {headers}")

        # 3. Processar a request
        response = await call_next(request)
        
        # 4. Registrar response
        logger.debug(f"Response: {method} {url} | Status: {response.status_code}")
        
        return response
