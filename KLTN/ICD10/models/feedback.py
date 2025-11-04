from django.db import models
from ICD10.models.icd10 import ICDDisease
from ICD10.models.user import User
from ICD10.models.chatbot import ChatSession, ChatMessage
from constants.constants import Constants


class Feedback_ICD10(models.Model):
    """
    Mô hình phản hồi của người dùng về mã bệnh ICD-10
    """
    disease = models.ForeignKey(ICDDisease, on_delete=models.CASCADE, related_name="feedbacks")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feedbacks")
    status = models.PositiveSmallIntegerField(choices=Constants.FEEDBACK_STATUS, default=3)
    description = models.TextField(null=True, blank=True)  # Mô tả chi tiết về phản hồi
    symptoms = models.TextField(null=True, blank=True)  # Triệu chứng liên quan
    image = models.TextField(null=True, blank=True)  # URL hình ảnh (nếu có)
    reason = models.TextField(null=True, blank=True)  # Lý do gửi phản hồi
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.disease.code} - {self.user.username}"

    class Meta:
        verbose_name = 'Phản hồi về ICD-10'
        verbose_name_plural = 'Phản hồi về ICD-10'
        app_label = "ICD10"
        db_table = "icd_feedback"
        ordering = ["-created_at"]
        
class Feedback_Chatbot(models.Model):
    """
    Mô hình phản hồi của người dùng về chatbot
    """
    chat_message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name="feedbacks")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatbot_feedbacks")
    status = models.PositiveSmallIntegerField(choices=Constants.FEEDBACK_STATUS, default=3)
    rating = models.IntegerField(null=True, blank=True)  # Đánh giá từ 1-5
    comments = models.TextField(null=True, blank=True)  # Bình luận thêm
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback from {self.user.username} on message {self.chat_message.id}"

    class Meta:
        verbose_name = 'Phản hồi về Chatbot'
        verbose_name_plural = 'Phản hồi về Chatbot'
        app_label = "ICD10"
        db_table = "icd_feedback_chatbot"
        ordering = ["-created_at"]