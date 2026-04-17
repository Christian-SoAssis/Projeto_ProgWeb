from typing import Any
from arq import create_pool
from arq.connections import RedisSettings
from app.domain.services.task_queue import TaskQueue
from app.core.config import settings

class ArqTaskQueue(TaskQueue):
    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.redis_url = redis_url

    async def enqueue(self, task_name: str, *args: Any, **kwargs: Any) -> None:
        redis = await create_pool(RedisSettings.from_dsn(self.redis_url))
        await redis.enqueue_job(task_name, *args, **kwargs)
        # Em uma implementação real, poderíamos manter o pool aberto.
