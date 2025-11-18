from django.db import models
from ICD10.models.icd10 import *
from ICD10.models.user import User
from ICD10.models.chatbot import ChatSession, ChatMessage
from constants.constants import Constants


class Feedback_ICD10(models.Model):
    """
    Mô hình phản hồi của người dùng về mã bệnh ICD-10 (chapter, block, disease)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feedbacks")
    
    disease = models.ForeignKey(ICDDisease, on_delete=models.CASCADE, related_name="feedbacks", null=True, blank=True)
    block = models.ForeignKey(ICDBlock, on_delete=models.CASCADE, related_name="feedbacks", null=True, blank=True)
    chapter = models.ForeignKey(ICDChapter, on_delete=models.CASCADE, related_name="feedbacks", null=True, blank=True)
    code = models.CharField(max_length=10, null=True, blank=True)  # Mã bệnh ICD-10 liên quan
    title_vi = models.CharField(max_length=255, null=True, blank=True)  # Tên bệnh tiếng Việt liên quan
    status = models.PositiveSmallIntegerField(choices=Constants.FEEDBACK_STATUS, default=3)
    reason = models.TextField(null=True, blank=True)  # Lý do gửi phản hồi
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.chapter:
            return f"{self.chapter.code} - {self.user.username}"
        elif self.block:
            return f"{self.block.code} - {self.user.username}"
        else:
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