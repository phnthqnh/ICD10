from django.contrib import admin
from ICD10.models.icd10 import *
from ICD10.models.user import *
from ICD10.models.chatbot import *
from ICD10.models.feedback import Feedback_Chapter, Feedback_Block, Feedback_Disease, Feedback_Chatbot
from ICD10.models.notification import Notification
from ICD10.models.login_event import LoginEvent
from ICD10.models.token_usage import TokenUsage
from ICD10.models.api_request_log import ApiRequestLog
# Register your models here.
from django.db import models
from unfold.admin import ModelAdmin
from .forms import UserCreationForm, UserChangeForm, CustomPasswordChangeForm
from utils.utils import Utils
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from ICD10.services.user.user_service import UserService
from ICD10.services.notification.notif_service import notify_user_feedback
from ICD10.services.feedback.disease_fb_service import DiseaseFeedbackService
from ICD10.services.feedback.block_fb_service import BlockFeedbackService
from ICD10.services.feedback.chapter_fb_service import ChapterFeedbackService
from ICD10.services.feedback.chatbot_fb_service import ChatbotFeedbackService

@admin.register(User)
class UserAdmin(ModelAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    change_password_form = CustomPasswordChangeForm
    model = User

    list_display = ("username", "email", "role", "status", "is_verified_doctor", "is_superuser")
    list_filter = ("status", "is_staff", "is_superuser", "role")
    search_fields = ("email", "username")
    readonly_fields = ("created_at", "last_login", "verification_image_tag", "avatar_tag")
    
    list_per_page = 20
    show_full_result_count = False

    fieldsets = (
        ("Thông tin cá nhân", {"fields": ("username", "email", "password", "first_name", "last_name", "avatar", "avatar_tag")}),
        ("Trạng thái", {"fields": ("status", "email_verified")}),
        ("Vai trò", {"fields": ("role", "is_verified_doctor", "license_number", "hospital", "verification_file", "verification_image_tag")}),
        ("Quyền", {"fields": ("is_staff", "is_superuser")}),
        ("Mốc thời gian", {"fields": ("created_at", "last_login")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "role", "status", "is_staff", "is_superuser"),
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
    
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        
        # Custom fieldsets cho change password form
        if request.path.endswith('password'):
            return [
                ('Thay đổi mật khẩu', {
                    'description': 'Để đảm bảo an toàn, hãy nhập mật khẩu cũ của bạn trước khi đặt mật khẩu mới.',
                    'fields': ('old_password', 'new_password1', 'new_password2'),
                }),
            ]
            
        return super().get_fieldsets(request, obj)
    
    def save_model(self, request, obj, form, change):
        UserService.handle_role_by_doctor_status(obj)
        if change:
            old_obj = User.objects.get(pk=obj.pk)

            # 🔥 false → true
            if not old_obj.is_verified_doctor and obj.is_verified_doctor:
                UserService.notify_doctor_verified(obj)
        super().save_model(request, obj, form, change)
        # Gửi email sau khi admin tạo user
        if not change:
            raw_password = getattr(form, "raw_password", None)
            UserService.send_activation_email_for_new_user(obj, raw_password)
        
        # if obj.is_verified_doctor:
        #     UserService.notify_doctor_verified(obj)

@admin.register(ICDChapter)
class ICDChapterAdmin(ModelAdmin):
    list_display = ("chapter", "code", "title_vi")
    search_fields = ("chapter", "code", "title_vi")
    list_per_page = 20
    show_full_result_count = False
    
    fieldsets = (
        ("Thông tin chương", {"fields": ("chapter", "code", "title_vi", "description")}),
    )
    
@admin.register(ICDBlock)
class ICDBlockAdmin(ModelAdmin):
    list_display = ("code", "title_vi", "chapter")
    search_fields = ("code", "title_vi", "chapter__code", "chapter__title_vi")
    list_filter = ("chapter",)
    autocomplete_fields= ('chapter',)
    list_per_page = 20
    show_full_result_count = False

    fieldsets = (
        ("Thông tin nhóm bệnh", {"fields": ("code", "title_vi", "description")}),
        ("Thuộc chương", {"fields": ("chapter",)}),
    )
    
@admin.register(ICDDisease)
class ICDDiseaseAdmin(ModelAdmin):
    list_display = ("code", "code_no_sign", "title_vi", "block", "parent")
    search_fields = ("code", "code_no_sign", "title_vi", "block__code", "block__title_vi")
    list_filter = ("block",)
    list_per_page = 20
    show_full_result_count = False
    autocomplete_fields= ('parent', 'block',)
    readonly_fields = ("updated_at",)
    
    fieldsets = (
        ("Thông tin bệnh", {"fields": ("code", "code_no_sign", "title_vi", "parent", "updated_at")}),
        ("Thuộc nhóm bệnh", {"fields": ("block",)}),
    )
    
    
@admin.register(ChatSession)
class ChatSessionAdmin(ModelAdmin):
    list_display = ("user", "title", "created_at", "updated_at")
    search_fields = ("user__username", "user__email", "title")
    list_filter = ("user__username",)
    list_per_page = 20
    show_full_result_count = False
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Thông tin phiên chat", {"fields": ("title", "user", "adk_session_id", "summary_count", "created_at", "updated_at")}),
    )
    
    
@admin.register(ChatMessage)
class ChatMessageAdmin(ModelAdmin):
    list_display = ("session", "role", "created_at")
    search_fields = ("session__title", "session__user__username", "session__user__email", "content")
    list_filter = ("role", "session__user__username")
    list_per_page = 20
    show_full_result_count = False
    fieldsets = (
        (None, {"fields": ("session", "role", "content", "image", "image_tag", "created_at")}),
    )
    readonly_fields = ("created_at", "image_tag")
    
    
class BaseFeedbackAdmin(ModelAdmin):
    """
    Base admin cho tất cả feedback
    """

    list_filter = ("status", "created_at")
    ordering = ("-created_at",)
    list_per_page = 20
    show_full_result_count = False
    readonly_fields = ("created_at", "get_user_info")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
        )

    # @admin.display(description="Người gửi")
    # def get_user_info(self, obj):
    #     return format_html(
    #         "<b>{}</b><br/>{}",
    #         obj.user.username,
    #         obj.user.email,
    #     )

@admin.register(Feedback_Chapter)
class FeedbackChapterAdmin(BaseFeedbackAdmin):
    list_display = (
        "id",
        "get_chapter",
        "user",
        "status",
        "created_at",
    )
    search_fields = ("user__username", "user__email", "chapter__code", "chapter__title_vi")
    list_filter = ("status", "created_at")
    readonly_fields = ("created_at",)
    
    fieldsets = (
        ("Thuộc chương", {"fields": ("user", "chapter", "status", "created_at")}),
        ("Nội dung phản hồi", {"fields": ("code", "title_vi", "type_feedback", "reason")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("chapter", "user")

    @admin.display(description="Chương")
    def get_chapter(self, obj):
        return f"{obj.chapter.code} - {obj.chapter.title_vi}"
    
    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Feedback_Chapter.objects.get(pk=obj.pk)

            # 🔥 false → true
            if old_obj.status != obj.status:
                ChapterFeedbackService.handle(obj)
        super().save_model(request, obj, form, change)
        
        

@admin.register(Feedback_Block)
class FeedbackBlockAdmin(BaseFeedbackAdmin):
    list_display = (
        "id",
        "get_block",
        "user",
        "status",
        "created_at",
    )
    search_fields = ("user__username", "user__email", "block__code", "block__title_vi")
    list_filter = ("status", "created_at")
    readonly_fields = ("created_at", "chapter")
    
    fieldsets = (
        ("Thuộc nhóm bệnh", {"fields": ("user", "block", "chapter", "status", "created_at")}),
        ("Nội dung phản hồi", {"fields": ("code", "title_vi", "type_feedback", "reason")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("block", "user")

    @admin.display(description="Nhóm bệnh")
    def get_block(self, obj):
        return f"{obj.block.code} - {obj.block.title_vi}"
    
    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Feedback_Block.objects.get(pk=obj.pk)

            # 🔥 false → true
            if old_obj.status != obj.status:
                BlockFeedbackService.handle(obj)
        super().save_model(request, obj, form, change)
        # BlockFeedbackService.handle(obj)

@admin.register(Feedback_Disease)
class FeedbackDiseaseAdmin(BaseFeedbackAdmin):
    list_display = (
        "id",
        "get_disease",
        "user",
        "status",
        "created_at",
    )
    search_fields = ("user__username", "user__email", "disease__code", "disease__title_vi")
    list_filter = ("status", "created_at")
    readonly_fields = ("created_at", "disease", "disease_parent", "block")
    
    fieldsets = (
        ("Thuộc mã bệnh", {"fields": ("user", "disease", "disease_parent", "block", "status", "created_at")}),
        ("Nội dung phản hồi", {"fields": ("code", "title_vi", "type_feedback", "reason")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("disease", "user")

    @admin.display(description="Bệnh")
    def get_disease(self, obj):
        return f"{obj.disease.code} - {obj.disease.title_vi}"
    
    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Feedback_Disease.objects.get(pk=obj.pk)

            # 🔥 false → true
            if old_obj.status != obj.status:
                DiseaseFeedbackService.handle(obj)
        super().save_model(request, obj, form, change)
        # DiseaseFeedbackService.handle(obj)


@admin.register(Feedback_Chatbot)
class FeedbackChatbotAdmin(BaseFeedbackAdmin):
    list_display = (
        "id",
        "get_username",
        "get_message_short",
        "rating",
        "created_at",
    )
    search_fields = ("chat_message__id", "chat_message__content")
    list_filter = ("created_at", "rating")
    list_per_page = 20
    show_full_result_count = False
    readonly_fields = (
        "chat_message",
        "get_user_info",
        "created_at", "replied_at")
    
    fieldsets = (
        ("Tin nhắn", {"fields": ("get_user_info", "chat_message",)}),
        ("Phản hồi của người dùng", {"fields": ("rating", "comments", "created_at",)}),
        ("Phản hồi của quản trị viên", {"fields": ("admin_reply", "replied_at",)}),
    )
    
    @admin.display(description="Người dùng")
    def get_username(self, obj):
        user = obj.chat_message.session.user
        return user.username if user else "-"

    @admin.display(description="Nội dung chat")
    def get_message_short(self, obj):
        content = obj.chat_message.content
        if not content:
            return "-"
        return content[:20] + "..." if len(content) > 20 else content

    @admin.display(description="Thông tin người dùng")
    def get_user_info(self, obj):
        user = obj.chat_message.session.user
        if not user:
            return "-"

        return format_html(
            """
            <b>Username:</b> {}<br/>
            <b>Email:</b> {}<br/>
            <b>User ID:</b> {}
            """,
            user.username,
            user.email,
            user.id,
        )

    def get_queryset(self, request):
        """
        Tối ưu query để tránh N+1
        """
        return (
            super()
            .get_queryset(request)
            .select_related(
                "chat_message",
                "chat_message__session",
                "chat_message__session__user",
            )
        )
        
    def save_model(self, request, obj, form, change):
        if "admin_reply" in form.changed_data:
            ChatbotFeedbackService.handle_admin_reply(obj, obj.admin_reply)

    
@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ("title", "recipient", "notif_type", "is_read", "created_at")
    list_filter = ("notif_type", "is_read", "recipient")
    search_fields = ("title", "message", "recipient__username")
    readonly_fields = ("created_at",)
    
    list_per_page = 20
    show_full_result_count = False
    
    fieldsets = (
        ("Người nhận", {"fields": ("recipient",)}),
        ("Thông tin thông báo", {"fields": ("title", "message", "url", "notif_type", "is_read", "created_at")}),
    )
    
    
    # khi mở change form, đánh dấu là đã đọc
    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Mark notification as read when opening change form
        notification = self.get_object(request, object_id)
        if notification and not notification.is_read:
            if request.user.is_superuser and notification.recipient == request.user:
                notification.is_read = True
                notification.save()
        return super().change_view(request, object_id, form_url, extra_context)
    
@admin.register(LoginEvent)
class LoginEventAdmin(ModelAdmin):
    list_display = ("user", "status", "ip_adress", "device", "created_at")
    search_fields = ("user__username", "user__email", "ip_adress", "device", "identifier")
    list_filter = ("status", "created_at")
    readonly_fields = ("created_at",)
    list_per_page = 20
    show_full_result_count = False
    
    fieldsets = (
        ("Thông tin sự kiện đăng nhập", {"fields": ("user", "status", "ip_adress", "user_agent", "device", "identifier", "created_at")}),
    )
    
@admin.register(TokenUsage)
class TokenUsageAdmin(ModelAdmin):
    list_display = ("user", "session", "input_tokens", "created_at")
    search_fields = ("user__username", "user__email", "session__title", "model")
    list_filter = ("model", "date", "created_at")
    readonly_fields = ("created_at",)
    list_per_page = 20
    show_full_result_count = False
    
    fieldsets = (
        ("Thông tin sử dụng token", {"fields": ("user", "session", "model", "input_tokens", "output_tokens", "total_tokens", "created_at")}),
    )
    
@admin.register(ApiRequestLog)
class ApiRequestLogAdmin(ModelAdmin):
    list_display = ("user", "path", "method", "status_code", "created_at")
    search_fields = ("user__username", "user__email", "path", "method", "status_code")
    list_filter = ("method", "status_code", "created_at")
    readonly_fields = ("created_at",)
    list_per_page = 20
    show_full_result_count = False
    
    fieldsets = (
        ("Thông tin log API", {"fields": ("user", "path", "method", "status_code", "response_time_ms", "ip_address", "user_agent", "created_at")}),
    )