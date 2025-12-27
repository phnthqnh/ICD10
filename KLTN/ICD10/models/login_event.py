from django.db import models
from ICD10.models.user import User
from constants.constants import Constants

class LoginEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='login_events', verbose_name="Người dùng")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    status = models.CharField(
        max_length=20,
        choices=Constants.LOGIN_STATUS_CHOICES,
        default="SUCCESS", verbose_name="Trạng thái đăng nhập"
    )
    ip_adress = models.GenericIPAddressField(null=True, blank=True, verbose_name="Địa chỉ IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    device = models.CharField(max_length=255, null=True, blank=True, verbose_name="Thiết bị")
    identifier = models.CharField(max_length=255, null=True, blank=True, help_text="Email hoặc username dùng để login", verbose_name="Định danh đăng nhập")
    def __str__(self):
        return f"{self.user.username} logged in at {self.created_at}"
    class Meta:
        db_table = 'login_event'
        ordering = ['-created_at']
        verbose_name = 'Sự kiện đăng nhập'
        verbose_name_plural = 'Sự kiện đăng nhập'
        