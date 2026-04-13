import asyncio
import logging
from functools import wraps
from typing import Callable, Any, Type, Tuple

logger = logging.getLogger(__name__)

def retry_with_backoff(
    retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator para retry com backoff exponencial.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            for i in range(retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if i == retries:
                        logger.error(f"Falha definitiva após {retries} tentativas: {str(e)}")
                        raise e
                    
                    logger.warning(f"Tentativa {i+1} falhou. Retentando em {delay}s... Erro: {str(e)}")
                    await asyncio.sleep(delay)
                    delay *= backoff_factor
            return None
        return wrapper
    return decorator
