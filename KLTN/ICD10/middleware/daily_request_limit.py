import datetime
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from libs.Redis import RedisWrapper

# Giới hạn request mỗi user mỗi ngày
DAILY_REQUEST_LIMIT = 30  # Tự chỉnh

class DailyRequestLimitMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # Chỉ áp dụng cho API chatbot
        if not request.path.startswith("/api/chat_with_ai"):
            return None

        if not request.user or not request.user.is_authenticated:
            return None

        user_id = request.user.id

        # Key lưu request count theo ngày
        date_str = datetime.date.today().isoformat()
        redis_key = f"daily_req:{user_id}:{date_str}"

        # ---- Lấy số request đã dùng ----
        count = RedisWrapper.get(redis_key)
        count = int(count) if count else 0

        # ---- Nếu vượt quá giới hạn ----
        if count >= DAILY_REQUEST_LIMIT:
            return JsonResponse({
                "error": "Bạn đã dùng hết lượt chat trong ngày. Vui lòng quay lại ngày mai."
            }, status=429)

        # ---- Tăng số lượng request ----
        RedisWrapper.incr(redis_key)

        # Set expiry = 24h (để tự reset ngày hôm sau)
        RedisWrapper.expire(redis_key, 86400)

        return None
