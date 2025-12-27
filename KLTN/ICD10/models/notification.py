# ICD10/models.py

from django.db import models
from django.contrib.auth import get_user_model
from ICD10.models.user import User
from constants.constants import Constants

class Notification(models.Model):
    
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications", verbose_name="Người nhận"
    )
    title = models.CharField(max_length=255, verbose_name="Tiêu đề")
    message = models.TextField(verbose_name="Nội dung thông báo")
    url = models.URLField(max_length=255, null=True, blank=True, verbose_name="Liên kết")
    notif_type = models.CharField(max_length=50, choices=Constants.NOTIFICATION_TYPE_CHOICES, default='system', verbose_name="Loại thông báo")
    is_read = models.BooleanField(default=False, verbose_name="Đã đọc")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'notifications'
        verbose_name = "Thông báo"
        verbose_name_plural = "Thông báo"
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
