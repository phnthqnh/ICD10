import time
import logging

from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone

from ICD10.models.api_request_log import ApiRequestLog

logger = logging.getLogger(__name__)


class ApiRequestLogMiddleware(MiddlewareMixin):
    """
    Middleware log API request cho Technical Dashboard
    """

    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        try:
            self.log_request(request, response)
        except Exception as e:
            # Tuyệt đối không làm crash request
            logger.exception("Failed to log API request")

        return response

    def log_request(self, request, response):
        # Chỉ log API, bỏ admin / static
        if not request.path.startswith("/api/"):
            return

        # Thời gian xử lý
        response_time_ms = (
            time.time() - getattr(request, "_start_time", time.time())
        ) * 1000

        # User (nếu đã login)
        user = request.user if request.user.is_authenticated else None

        # IP
        ip_address = self.get_client_ip(request)

        ApiRequestLog.objects.create(
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            response_time_ms=round(response_time_ms, 2),
            user=user,
            ip_address=ip_address,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            created_at=timezone.now(),
        )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")
