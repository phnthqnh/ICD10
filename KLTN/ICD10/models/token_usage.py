from django.db import models
from .user import User
from .chatbot import ChatSession

class TokenUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='token_usages', verbose_name="Người dùng")
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='token_usages', verbose_name="Phiên chatbot")
    date = models.DateField(auto_now_add=True, verbose_name="Ngày sử dụng")

    model = models.CharField(max_length=100, verbose_name="Mô hình AI")
    input_tokens = models.IntegerField(default=0, verbose_name="Số token đầu vào")
    output_tokens = models.IntegerField(default=0, verbose_name="Số token đầu ra")
    total_tokens = models.IntegerField(default=0, verbose_name="Tổng số token")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    def __str__(self):
        return f"{self.user.username} used {self.total_tokens} tokens at {self.created_at}"
    
    class Meta:
        db_table = 'token_usage'
        verbose_name='Token trong chatbot'
        verbose_name_plural='Token trong chatbot'