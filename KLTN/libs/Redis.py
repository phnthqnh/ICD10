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
        
    @staticmethod
    def incr(key: str, amount: int = 1) -> Optional[int]:
        """
        Tăng giá trị integer trong Redis.
        - Nếu key chưa tồn tại → set = amount.
        - Nếu key tồn tại nhưng không phải số → ghi đè thành amount.
        Trả về giá trị sau khi tăng.
        """
        try:
            # cache.incr chỉ hoạt động nếu key tồn tại và là int
            value = cache.get(key)

            if value is None:
                # Nếu key chưa tồn tại → khởi tạo
                cache.set(key, amount)
                return amount

            try:
                # Nếu là số thì tăng
                new_value = cache.incr(key, amount)
                return new_value
            except ValueError:
                # Nếu value không phải số → ghi đè lại
                cache.set(key, amount)
                return amount

        except Exception as e:
            logger.error(f"Redis incr error for key '{key}': {e}")
            return None
    
    @staticmethod
    def expire(key: str, seconds: int) -> bool:
        """
        Đặt TTL cho key (giống Redis EXPIRE).
        Chỉ hoạt động nếu backend cache là Redis.
        """
        try:
            client = cache.client.get_client()
            return client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis expire error for key '{key}': {e}")
            return False

