import re
from typing import Any, Dict

def sanitize_log(log_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize sensitive information from logs according to LGPD requirements.
    Masks CPF, CNPJ, Passwords and Authentication tokens.
    """
    sanitized = log_record.copy()
    
    # Redact Headers
    if "headers" in sanitized and isinstance(sanitized["headers"], dict):
        if "Authorization" in sanitized["headers"]:
            sanitized["headers"]["Authorization"] = "Bearer [REDACTED]"
            
    # Redact Body content
    if "body" in sanitized and isinstance(sanitized["body"], dict):
        body = sanitized["body"]
        
        # Redact password
        if "password" in body:
            body["password"] = "[REDACTED]"
            
        # Mask CPF/CNPJ if document_type and document_number are presents or if document field is found
        # Usually checking by keys or applying regex on values. We'll simply mask document_number directly.
        for key in ["document_number", "cpf", "cnpj"]:
            if key in body and isinstance(body[key], str):
                val = body[key]
                # CPF: 11 chars
                if len(val) == 11 and val.isdigit():
                    body[key] = "***.***.***-XX"
                # CNPJ: 14 chars
                elif len(val) == 14 and val.isdigit():
                    body[key] = "**.***.****/****-XX"
                else:
                    body[key] = "[REDACTED DOCUMENT]"
                    
    return sanitized

# Se estivermos utilizando FastAPI Request, podemos criar um Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

class LogSanitizerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Aqui capturariamos conteudo do log
        # O processamento real do body no middleware pode ser complexo (consume o stream)
        # O uso do sanitize_log(log_record) e a solucao primaria do requisito.
        response = await call_next(request)
        return response
