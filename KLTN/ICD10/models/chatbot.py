from django.db import models
from .user import User
from constants.constants import Constants

class ChatSession(models.Model):
    """
    Một session đại diện cho một chuỗi hội thoại giữa người dùng và chatbot.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_sessions")
    title = models.CharField(max_length=255, default="Cuộc hội thoại mới")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    summary_count = models.IntegerField(default=0)  # số lần đã tóm tắt

    def __str__(self):
        return f"ChatSession({self.id}) - {self.title}"
    
    class Meta:
        verbose_name = 'Phiên chat'
        verbose_name_plural = 'Phiên chat'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'created_at'], name='gemini_chat_user_time_idx'),
        ]


class ChatMessage(models.Model):
    """
    Một tin nhắn trong cuộc hội thoại.
    """

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10, choices=Constants.ROLE_CHAT)
    content = models.TextField()
    image = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:40]}"
    
    class Meta:
        verbose_name = 'Tin nhắn'
        verbose_name_plural = 'Tin nhắn'
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp'], name='gemini_msg_session_time_idx'),
        ]