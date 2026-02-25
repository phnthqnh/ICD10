from django.db import models
from ICD10.models.icd10 import *
from ICD10.models.user import User
from ICD10.models.chatbot import ChatSession, ChatMessage
from constants.constants import Constants


class Feedback_ICD10(models.Model):
    """
    Mô hình phản hồi của người dùng về mã bệnh ICD-10 (chapter, block, disease)
    """
    code = models.CharField(max_length=10, null=True, blank=True, verbose_name="Mã bệnh ICD-10")  # Mã bệnh ICD-10 liên quan
    title_vi = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tên bệnh")  # Tên bệnh tiếng Việt liên quan
    status = models.PositiveSmallIntegerField(choices=Constants.FEEDBACK_STATUS, default=3, verbose_name="Trạng thái phản hồi")
    type_feedback = models.PositiveSmallIntegerField(choices=Constants.FEEDBACK_TYPE, default=1, verbose_name="Loại phản hồi")
    reason = models.TextField(null=True, blank=True, verbose_name="Lý do gửi phản hồi")  # Lý do gửi phản hồi
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo phản hồi")
    

    class Meta:
        abstract = True
        
class Feedback_Chapter(Feedback_ICD10):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chapter_feedbacks", verbose_name="Người dùng")
    chapter = models.ForeignKey(ICDChapter, on_delete=models.CASCADE, related_name="feedbacks", verbose_name="Chương")

    def __str__(self):
        return f"{self.chapter.code}"
    class Meta:
        verbose_name = 'Phản hồi về Chương ICD-10'
        verbose_name_plural = 'Phản hồi về Chương ICD-10'
        app_label = "ICD10"
        db_table = "icd_feedback_chapter"
        ordering = ["-created_at"]
        
class Feedback_Block(Feedback_ICD10):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="block_feedbacks", verbose_name="Người dùng")
    block = models.ForeignKey(ICDBlock, on_delete=models.CASCADE, related_name="feedbacks", verbose_name="Nhóm bệnh")
    chapter = models.ForeignKey(ICDChapter, on_delete=models.CASCADE, related_name="block_feedbacks", null=True, blank=True, verbose_name="Chương")
    
    def __str__(self):
        return f"{self.block.code}"
    class Meta:
        verbose_name = 'Phản hồi về Nhóm ICD-10'
        verbose_name_plural = 'Phản hồi về Nhóm ICD-10'
        app_label = "ICD10"
        db_table = "icd_feedback_block"
        ordering = ["-created_at"]

class Feedback_Disease(Feedback_ICD10):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="disease_feedbacks", verbose_name="Người dùng")
    disease = models.ForeignKey(ICDDisease, on_delete=models.CASCADE, related_name="feedbacks", verbose_name="Mã bệnh")
    disease_parent = models.ForeignKey(ICDDisease, on_delete=models.CASCADE, related_name="child_disease_feedbacks", null=True, blank=True, verbose_name="Bệnh cha")
    block = models.ForeignKey(ICDBlock, on_delete=models.CASCADE, related_name="disease_feedbacks", null=True, blank=True, verbose_name="Nhóm bệnh")

    def __str__(self):
        return f"{self.disease.code}"
    class Meta:
        verbose_name = 'Phản hồi về Mã bệnh ICD-10'
        verbose_name_plural = 'Phản hồi về Mã bệnh ICD-10'
        app_label = "ICD10"
        db_table = "icd_feedback_disease"
        ordering = ["-created_at"]
        
class Feedback_Chatbot(models.Model):
    """
    Mô hình phản hồi của người dùng về chatbot
    """
    chat_message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name="feedbacks", verbose_name="Tin nhắn chatbot")
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatbot_feedbacks")
    status = models.PositiveSmallIntegerField(choices=Constants.FEEDBACK_STATUS, default=3, verbose_name="Trạng thái phản hồi")
    rating = models.IntegerField(null=True, blank=True, verbose_name="Đánh giá")  # Đánh giá từ 1-5
    comments = models.TextField(null=True, blank=True, verbose_name="Bình luận")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo phản hồi")
    
    admin_reply = models.TextField(null=True, blank=True, verbose_name="Phản hồi của quản trị viên")
    replied_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày phản hồi")
    
    def __str__(self):
        return f"{self.chat_message.id}"

    class Meta:
        verbose_name = 'Phản hồi về Chatbot'
        verbose_name_plural = 'Phản hồi về Chatbot'
        app_label = "ICD10"
        db_table = "icd_feedback_chatbot"
        ordering = ["-created_at"]