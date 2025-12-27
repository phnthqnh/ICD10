from django.db import models
from .user import User

class ApiRequestLog(models.Model):
    method = models.CharField(max_length=10, verbose_name="HTTP Method")
    path = models.CharField(max_length=255, verbose_name="Đường dẫn")

    status_code = models.IntegerField(verbose_name="HTTP Status Code")
    response_time_ms = models.FloatField(verbose_name="Thời gian phản hồi (ms)")

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Người dùng",
    )

    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Địa chỉ IP")
    user_agent = models.TextField(null=True, blank=True, verbose_name="User Agent")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        verbose_name="Nhật ký yêu cầu API"
        verbose_name_plural="Nhật ký yêu cầu API"
        db_table = "api_request_log"
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["status_code"]),
            models.Index(fields=["path"]),
        ]
