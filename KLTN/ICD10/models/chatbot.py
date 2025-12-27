from django.db import models
from .user import User
from constants.constants import Constants
from django.utils.html import format_html

class ChatSession(models.Model):
    """
    Một session đại diện cho một chuỗi hội thoại giữa người dùng và chatbot.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_sessions", verbose_name="Người dùng")
    title = models.CharField(max_length=255, default="Cuộc hội thoại mới", verbose_name="Tiêu đề")
    adk_session_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="ADK Session ID")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Thời gian cập nhật")
    summary_count = models.IntegerField(default=0, verbose_name="Số lần tóm tắt")  # số lần đã tóm tắt

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

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages", verbose_name="Phiên chat")
    role = models.CharField(max_length=10, choices=Constants.ROLE_CHAT, verbose_name="Vai trò")
    content = models.TextField(verbose_name="Nội dung")
    image = models.URLField(null=True, blank=True, verbose_name="Hình ảnh")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian tạo")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian")

    def __str__(self):
        return f"{self.role}: {self.content[:40]}"
    
    class Meta:
        verbose_name = 'Tin nhắn'
        verbose_name_plural = 'Tin nhắn'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at'], name='gemini_msg_session_time_idx'),
        ]
        
    def image_tag(self):
        if not self.image:
            return "—"
        return format_html("""
            <img src="{0}" style="max-height: 200px; cursor:pointer; border:1px solid #ccc; padding:4px;"
                onclick="document.getElementById('imgModal').style.display='block';
                        document.getElementById('imgModalContent').src='{0}'" />

            <div id="imgModal" style="
                display:none; position:fixed; z-index:9999; padding-top:100px;
                left:0; top:0; width:100%; height:100%; overflow:auto;
                background-color:rgba(0,0,0,0.8);">
                <span onclick="document.getElementById('imgModal').style.display='none'"
                    style="position:absolute; top:30px; right:50px; font-size:40px; color:white; cursor:pointer;">
                    &times;
                </span>
                <img id="imgModalContent" style="margin:auto; display:block; max-width:90%; max-height:90%;">
            </div>
            """, self.image
        )

    image_tag.short_description = "Xem ảnh"