import redis.asyncio as redis
from app.core.config import settings

# Redis client para tokens (DB 1)
tokens_redis = redis.from_url(
    f"{settings.REDIS_URL}/{settings.REDIS_TOKENS_DB}",
    decode_responses=True
)

# Redis client para filas (DB 0) - reservado para ARQ
queue_redis = redis.from_url(
    f"{settings.REDIS_URL}/{settings.REDIS_QUEUE_DB}",
    decode_responses=True
)
