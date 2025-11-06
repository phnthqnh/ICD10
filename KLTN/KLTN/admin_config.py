from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
import os
from django.apps import apps
import json

# Thay thế việc sử dụng reverse_lazy trực tiếp bằng một hàm trì hoãn
def get_admin_url(viewname, *args, **kwargs):
    """Trả về một hàm lambda để trì hoãn việc tạo URL cho đến khi cần thiết"""
    return lambda request=None: reverse_lazy(viewname, *args, **kwargs)

# Cấu hình cơ bản cho Unfold
UNFOLD = {
    "SITE_HEADER": "ICD10 Admin",
    "SITE_TITLE": "ICD10 Management",
    "SITE_SUBHEADER": "Hệ thống quản lý mã bệnh ICD10",
    "SITE_SYMBOL": "🧬",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "SHOW_BACK_BUTTON": True, # show/hide "Back" button on changeform in header, default: False
    "SITE_ICON": {
        "light": lambda request: static("logo.svg"),
        "dark": lambda request: static("logo.svg"),
    },
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/svg+xml",
            "href": lambda request: static("logo.svg"),
        },
    ],
    "LOGIN": {
        "image": lambda request: static("logo_bg.png"),
    },
    "BORDER_RADIUS": "8px",
    "STYLES": [
        lambda request: static("css/styles.css"),
    ],
    "CUSTOM_JS": ["js/admin_notifications.js"],
    "COLORS": {
        "primary": {
            "50": "#E3E8ED",
            "100": "#96CAF4",
            "200": "#5FA6E0",
            "300": "#598CB6",
            "400": "#316F9F",
            "500": "#4E7593",
            "600": "#305E81",
            "700": "#183856",  # ✅ Màu chủ đạo bạn muốn
            "800": "#132E44",
            "900": "#0E2433",
            "950": "#091A22",
        },
        # màu nền (base) có thể giữ nguyên hoặc đổi nhẹ cho phù hợp
        "base": {
            "50": "#F9FAFB",
            "100": "#F3F4F6",
            "200": "#E5E7EB",
            "300": "#D1D5DB",
            "400": "#9CA3AF",
            "500": "#6B7280",
            "600": "#4B5563",
            "700": "#374151",
            "800": "#1F2937",
            "900": "#111827",
            "950": "#0B0F14",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",  # text-base-500
            "subtle-dark": "var(--color-base-400)",  # text-base-400
            "default-light": "var(--color-base-600)",  # text-base-600
            "default-dark": "var(--color-base-300)",  # text-base-300
            "important-light": "var(--color-base-900)",  # text-base-900
            "important-dark": "var(--color-base-100)",  # text-base-100
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": _("Navigation"),
                "items": [
                    {
                        "title": _("Phản hồi về ICD10"),
                        "icon": "feedback",
                        "link": reverse_lazy("admin:ICD10_feedback_icd10_changelist"),
                    },
                    {
                        "title": _("Phản hồi về Chatbot"),
                        "icon": "3p",
                        "link": reverse_lazy("admin:ICD10_feedback_chatbot_changelist"),
                    },
                    {
                        "title": _("Thông báo"),
                        "icon": "notifications",
                        "link": reverse_lazy("admin:ICD10_notification_changelist"),
                        # "badge": "ICD10.views.notification_views.notification_badge_callback",
                    },
                ],
            },
            {
                "title": _("ICD10 Management"),
                "items": [
                    {
                        "title": _("Chương"),
                        "icon": "book_2",
                        "link": reverse_lazy("admin:ICD10_icdchapter_changelist"),
                    },
                    {
                        "title": _("Nhóm bệnh"),
                        "icon": "menu_book",
                        "link": reverse_lazy("admin:ICD10_icdblock_changelist"),
                    },
                    {
                        "title": _("Bệnh ICD10"),
                        "icon": "coronavirus",
                        "link": reverse_lazy("admin:ICD10_icddisease_changelist"),
                    },
                    {
                        "title": _("Thông tin bổ sung"),
                        "icon": "info",
                        "link": reverse_lazy("admin:ICD10_diseaseextrainfo_changelist"),
                    },
                ],
            },
            {
                "title": _("User Management"),
                "items": [
                    {
                        "title": _("Người dùng"),
                        "icon": "person",
                        "link": reverse_lazy("admin:ICD10_user_changelist"),
                    },
                    {
                        "title": _("Phiên chat"),
                        "icon": "chat_bubble",
                        "link": reverse_lazy("admin:ICD10_chatsession_changelist"),
                    },
                    {
                        "title": _("Tin nhắn"),
                        "icon": "message",
                        "link": reverse_lazy("admin:ICD10_chatmessage_changelist"),
                    },
                ],
            },
        ],
    },
    

}