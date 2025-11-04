from django.contrib import admin
from ICD10.models.icd10 import *
from ICD10.models.user import *
from ICD10.models.chatbot import *
from ICD10.models.feedback import *
from ICD10.models.notification import *
# Register your models here.
from django.db import models
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import ArrayWidget, WysiwygWidget
from .forms import UserCreationForm, UserChangeForm
from utils.utils import Utils
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@admin.register(User)
class UserAdmin(ModelAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User

    list_display = ("username", "email", "role", "status", "is_verified_doctor", "is_superuser")
    list_filter = ("status", "is_staff", "is_superuser", "role")
    search_fields = ("email", "username")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "last_login")

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Status", {"fields": ("status", "email_verified")}),
        ("Role", {"fields": ("role", "is_verified_doctor", "license_number", "hospital", "verification_file")}),
        ("Permissions", {"fields": ("is_staff", "is_superuser")}),
        ("Important dates", {"fields": ("created_at", "last_login")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "role", "status", "is_staff", "is_superuser"),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        """Phân biệt form tạo mới và form sửa"""
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        else:
            defaults["form"] = self.form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)
    
    def save_model(self, request, obj, form, change):
        # nếu is_verified_doctor = true thì role = 2
        if obj.is_verified_doctor:
            obj.role = 2  # doctor
        super().save_model(request, obj, form, change)
        # Gửi email sau khi admin tạo user
        if not change:
            raw_password = getattr(form, "raw_password", None)
            if raw_password:
                token = Utils.generate_verification_token(obj)
                activation_link = f"{settings.ACTIVATION_URL}?token={token}"
                Utils.admin_send_activation_email(
                    user=obj,
                    password=raw_password,
                    activation_link=activation_link
                )
        
        if obj.is_verified_doctor:
            Notification.objects.create(
                recipient=obj,
                title="Xác nhận bác sĩ thành công",
                message=f"Chúc mừng! Tài khoản bác sĩ của bạn đã được xác thực",
                notif_type='system'
            )
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{obj.id}",
                {
                    "type": "send_notification",
                    "event": "verification_doctor",
                    "message": f"Chúc mừng! Tài khoản bác sĩ của bạn đã được xác thực ✅",
                    "role": obj.role,
                },
            )

@admin.register(ICDChapter)
class ICDChapterAdmin(ModelAdmin):
    list_display = ("code", "title_vi", "description")
    search_fields = ("code", "title_vi")
    ordering = ("code",)
    list_per_page = 20
    
@admin.register(ICDBlock)
class ICDBlockAdmin(ModelAdmin):
    list_display = ("code", "title_vi", "chapter")
    search_fields = ("code", "title_vi", "chapter__code", "chapter__title_vi")
    ordering = ("code",)
    list_filter = ("chapter",)
    list_per_page = 20
    
    
class DiseaseExtraInfoInline(admin.StackedInline):
    model = DiseaseExtraInfo
    extra = 0  # không tạo thêm dòng trống
    can_delete = False
    classes = ["unfold-card", "collapse"]  # 👈 Thêm class để hiển thị đẹp hơn
    show_change_link = False
    # fieldsets = (
    #     ("Thông tin thêm", {
    #         "fields": ("description", "symptoms", "wikipedia_url", "image_url"),
    #     }),
    # )
    fields = ("description", "symptoms", "wikipedia_url", "image_url")
    
@admin.register(ICDDisease)
class ICDDiseaseAdmin(ModelAdmin):
    list_display = ("code", "code_no_sign", "title_vi", "block", "parent")
    search_fields = ("code", "code_no_sign", "title_vi", "block__code", "block__title_vi")
    ordering = ("code",)
    list_filter = ("block", "parent")
    list_per_page = 20
    readonly_fields = ("updated_at",)
    
    inlines = [DiseaseExtraInfoInline]
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:  # Nếu tạo mới bệnh
            try:
                Utils.add_new_disease_embedding(obj.code)
                self.message_user(request, f"Đã thêm embedding cho bệnh {obj.code} thành công")
            except Exception as e:
                self.message_user(request, f"Lỗi khi thêm embedding: {str(e)}", level='ERROR')

    
@admin.register(DiseaseExtraInfo)
class DiseaseExtraInfoAdmin(ModelAdmin):
    list_display = ("disease", "wikipedia_url",)
    search_fields = ("disease__code", "disease__title_vi", "image_url")
    ordering = ("disease__code",)
    list_per_page = 20
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        try:
            Utils.reembed_disease(obj.disease.code)
            self.message_user(request, f"Đã cập nhật embedding cho bệnh {obj.disease.code} thành công")
        except Exception as e:
            self.message_user(request, f"Lỗi khi cập nhật embedding: {str(e)}", level='ERROR')


@admin.register(ChatSession)
class ChatSessionAdmin(ModelAdmin):
    list_display = ("user", "title", "created_at", "updated_at")
    search_fields = ("user__username", "user__email", "title")
    ordering = ("-created_at",)
    list_filter = ("user__username",)
    list_per_page = 20
    readonly_fields = ("created_at", "updated_at")
    
@admin.register(ChatMessage)
class ChatMessageAdmin(ModelAdmin):
    list_display = ("session", "role", "created_at")
    search_fields = ("session__title", "session__user__username", "session__user__email", "content")
    ordering = ("-created_at",)
    list_filter = ("role", "session__user__username")
    list_per_page = 20
    readonly_fields = ("created_at",)
    
@admin.register(Feedback_ICD10)
class FeedbackICD10Admin(ModelAdmin):
    list_display = ("disease__code", "user", "status", "created_at")
    search_fields = ("disease__code", "user__username", "user__email")
    ordering = ("-created_at",)
    list_filter = ("status", "created_at")
    list_per_page = 20
    readonly_fields = ("created_at",)
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        channel_layer = get_channel_layer()
        
        # thay đổi trạng thái hoặc xử lý khác nếu cần thiết khi tạo mới phản hồi từ admin
        if obj.status == 1:
            # Thông báo cho người dùng
            Notification.objects.create(
                recipient=obj.user,
                title="Phản hồi ICD-10 được chấp nhận",
                message=f"Phản hồi về {obj.disease.code} đã được chấp nhận",
                notif_type='system'
            )
            async_to_sync(channel_layer.group_send)(
                f"user_{obj.user.id}",
                {
                    "type": "send_notification",
                    "event": "feedback_update",
                    "message": f"Phản hồi về {obj.disease.code} đã được chấp nhận ✅",
                    "feedback_id": obj.id,
                },
            )
            # Cập nhật thông tin bệnh theo phản hồi
            disease = obj.disease
            disease_extra, created = DiseaseExtraInfo.objects.get_or_create(disease=disease)
            if obj.description:
                disease_extra.description = obj.description
            if obj.symptoms:
                disease_extra.symptoms = obj.symptoms
            if obj.image:
                disease_extra.image = obj.image
            disease_extra.save()
            
            # Reembedding sau khi cập nhật thông tin
            try:
                Utils.reembed_disease(disease.code)
                self.message_user(request, f"Đã cập nhật embedding cho bệnh {disease.code} thành công")
            except Exception as e:
                self.message_user(request, f"Lỗi khi cập nhật embedding: {str(e)}", level='ERROR')
            
        if obj.status == 2:
            # Thông báo cho người dùng
            Notification.objects.create(
                recipient=obj.user,
                title="Phản hồi ICD-10 bị từ chối",
                message=f"Phản hồi về {obj.disease.code} đã bị từ chối",
                notif_type='system'
            )
            async_to_sync(channel_layer.group_send)(
                f"user_{obj.user.id}",
                {
                    "type": "send_notification",
                    "event": "feedback_update",
                    "message": f"Phản hồi về {obj.disease.code} đã bị từ chối ❌",
                    "feedback_id": obj.id,
                },
            )
    
@admin.register(Feedback_Chatbot)
class FeedbackChatbotAdmin(ModelAdmin):
    list_display = ("chat_message", "user", "status", "created_at")
    search_fields = ("chat_message__id", "user__username", "user__email")
    ordering = ("-created_at",)
    list_filter = ("status", "created_at")
    list_per_page = 20
    readonly_fields = ("created_at",)
    
@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ("title", "recipient", "notif_type", "is_read", "created_at")
    list_filter = ("notif_type", "is_read", "created_at")
    search_fields = ("title", "message", "recipient__username")
    readonly_fields = ("created_at",)
    
    # khi mở change form, đánh dấu là đã đọc
    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Mark notification as read when opening change form
        notification = self.get_object(request, object_id)
        if notification and not notification.is_read:
            if request.user.is_superuser and notification.recipient == request.user:
                notification.is_read = True
                notification.save()
        return super().change_view(request, object_id, form_url, extra_context)