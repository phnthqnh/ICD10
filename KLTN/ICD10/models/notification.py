# ICD10/models.py

from django.db import models
from django.contrib.auth import get_user_model
from ICD10.models.user import User
from constants.constants import Constants

class Notification(models.Model):
    
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    url = models.CharField(max_length=255, null=True, blank=True)
    notif_type = models.CharField(max_length=20, choices=Constants.NOTIFICATION_TYPE_CHOICES, default='system')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'notifications'
        verbose_name = "Thông báo"
        verbose_name_plural = "Thông báo"
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
