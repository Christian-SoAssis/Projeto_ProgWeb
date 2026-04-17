from abc import ABC, abstractmethod
from typing import Any

class TaskQueue(ABC):
    @abstractmethod
    async def enqueue(self, task_name: str, *args: Any, **kwargs: Any) -> None:
        """Enqueues a task for background processing."""
        pass
