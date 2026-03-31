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

        # Mask CPF/CNPJ
        for key in ["document_number", "cpf", "cnpj"]:
            if key in body and isinstance(body[key], str):
                val = body[key]
                if len(val) == 11 and val.isdigit():
                    body[key] = "***.***.***-XX"
                elif len(val) == 14 and val.isdigit():
                    body[key] = "**.***.****/****-XX"
                else:
                    body[key] = "[REDACTED DOCUMENT]"

    return sanitized


# Middleware ASGI puro — evita o bug conhecido do BaseHTTPMiddleware com asyncpg/asyncio
# onde Tasks pendentes corrompem o pool de conexões durante tratamento de exceções HTTP.
class LogSanitizerMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)
