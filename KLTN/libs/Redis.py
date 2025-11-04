from django.core.cache import cache
import json
from typing import Any, Optional
import logging


logger = logging.getLogger(__name__)


class RedisWrapper:
    @staticmethod
    def save(key: str, value: Any, expire_time: int = None) -> bool:
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            cache.set(key, value, timeout=expire_time)
            return True
        except Exception as e:
            logger.error(f"Redis save error: {e}")
            return False

    @staticmethod
    def get(key: str) -> Optional[Any]:
        try:
            value = cache.get(key)
            if value is None:
                return None
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    @staticmethod
    def remove(key: str) -> bool:
        try:
            cache.set(key, None, timeout=1)
            return True
        except Exception as _:
            logger.error(f"Redis remove error")
            return False

    @staticmethod
    def ttl(key: str) -> int:
        try:
            return cache.ttl(key)
        except Exception as e:
            logger.error(f"Redis ttl error: {e}")
            return -1
        
    @staticmethod
    def pipeline(transaction: bool = False):
        try:
            return cache.client.get_client().pipeline(transaction=transaction)
        except Exception as e:
            logger.error(f"Redis pipeline error: {e}")
            return None

    @staticmethod
    def hgetall(key: str):
        """Lấy toàn bộ hash key từ Redis (trả về dict {field: value})"""
        try:
            client = cache.client.get_client()
            raw = client.hgetall(key)
            return {k.decode(): v.decode() for k, v in raw.items()}
        except Exception as e:
            logger.error(f"Redis hgetall error: {e}")
            return {}
