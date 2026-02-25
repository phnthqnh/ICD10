import datetime
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from libs.Redis import RedisWrapper

from rest_framework_simplejwt.authentication import JWTAuthentication
from django.urls import resolve

# Giới hạn request mỗi user mỗi ngày
DAILY_REQUEST_LIMIT = 20  # Tự chỉnh

logger = logging.getLogger(__name__)


class DailyRequestLimitMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # Chỉ áp dụng cho API chatbot
        try:
            resolver = resolve(request.path)
            if resolver.url_name != "chat-with-ai":
                return None
        except Exception:
            return None

        user_id = None

        # If Django set an authenticated user (session-based), use it
        if getattr(request, "user", None) and request.user.is_authenticated:
            user_id = request.user.id

        # If not authenticated at middleware stage (e.g. JWT auth used by DRF),
        # try to read user id from Authorization Bearer token
        if user_id is None:
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.split()[1]
                try:
                    auth = JWTAuthentication()
                    validated_token = auth.get_validated_token(token)
                    user_id = validated_token["user_id"]
                except Exception:
                    return None

        # If still no user id, skip limiting here (could alternatively limit by IP)
        if not user_id:
            logger.debug("DailyRequestLimit: no user_id found, skipping limit")
            return None

        # Key lưu request count theo ngày
        today = datetime.date.today().isoformat()
        redis_key = f"daily_req:{user_id}:{today}"

        # ---- Lấy số request đã dùng ----
        count = RedisWrapper.incr(redis_key)
        
        if count is None:
            logger.error("Redis incr failed")
            return JsonResponse(
                {"error": "Hệ thống đang bận, vui lòng thử lại sau"},
                status=503
            )


        if count == 1:
            # set TTL tới 0h
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            seconds = int(
                datetime.datetime.combine(tomorrow, datetime.time.min).timestamp()
                - datetime.datetime.now().timestamp()
            )
            RedisWrapper.expire(redis_key, seconds)

        if count > DAILY_REQUEST_LIMIT:
            return JsonResponse(
                {"error": "Bạn đã dùng hết lượt chat trong ngày"},
                status=429
            )
