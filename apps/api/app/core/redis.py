"""
Redis connection factory.

Os clientes Redis NÃO são instanciados no nível do módulo para evitar que fiquem
amarrados ao event loop de importação (incompatível com pytest-asyncio que cria um
novo loop por teste). Em vez disso, são criados dentro do lifespan da aplicação e
expostos via app.state.
"""
import redis.asyncio as aioredis
from app.core.config import settings


def create_tokens_redis() -> aioredis.Redis:
    """Cria um novo cliente Redis para tokens (DB 1)."""
    return aioredis.from_url(
        f"{settings.REDIS_URL}/{settings.REDIS_TOKENS_DB}",
        decode_responses=True,
    )


def create_queue_redis() -> aioredis.Redis:
    """Cria um novo cliente Redis para filas/ARQ (DB 0)."""
    return aioredis.from_url(
        f"{settings.REDIS_URL}/{settings.REDIS_QUEUE_DB}",
        decode_responses=True,
    )
