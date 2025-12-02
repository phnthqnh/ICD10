# ICD10/middleware.py
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from ICD10.models.user import User
from urllib.parse import parse_qs
import jwt
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user_from_token(token):
    """
    Lấy user từ JWT token
    """
    try:
        # Decode JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        
        if not user_id:
            logger.warning("Token không chứa user_id")
            return AnonymousUser()
        
        # Lấy user từ database
        user = User.objects.get(id=user_id)
        logger.info(f"JWT Auth successful for user: {user.username}")
        return user
        
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token đã hết hạn")
        return AnonymousUser()
    except jwt.DecodeError:
        logger.warning("JWT token không hợp lệ")
        return AnonymousUser()
    except User.DoesNotExist:
        logger.warning(f"User với id {user_id} không tồn tại")
        return AnonymousUser()
    except Exception as e:
        logger.error(f"Lỗi khi decode JWT: {str(e)}")
        return AnonymousUser()


class HybridAuthMiddleware(BaseMiddleware):
    """
    Middleware hỗ trợ cả JWT và Session authentication
    - JWT: Dùng cho Angular frontend (token trong query string)
    - Session: Dùng cho Django Admin (session cookies)
    """
    
    async def __call__(self, scope, receive, send):
        # Parse query string để lấy token
        query_string = scope.get('query_string', b'').decode()
        params = parse_qs(query_string)
        token = params.get('token', [None])[0]
        
        if token:
            # Nếu có token, dùng JWT authentication
            logger.info("Attempting JWT authentication")
            scope['user'] = await get_user_from_token(token)
            scope['auth_type'] = 'jwt'
        else:
            # Không có token, dùng session authentication (Django Admin)
            logger.info("Attempting session authentication")
            from channels.auth import get_user
            scope['user'] = await get_user(scope)
            scope['auth_type'] = 'session'
        
        # Log kết quả authentication
        user = scope['user']
        if user.is_authenticated:
            logger.info(f"Authentication successful: {user.username} ({scope['auth_type']})")
        else:
            logger.warning(f"Authentication failed ({scope['auth_type']})")
            
        return await super().__call__(scope, receive, send)