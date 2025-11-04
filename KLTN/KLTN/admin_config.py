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
    "SITE_TITLE": "ICD10 Admin",
    "SITE_HEADER": "ICD10 Management",
    "SITE_SUBHEADER": "Hệ thống quản lý mã bệnh ICD10",
    "SITE_ICON": None,
    "SITE_LOGO": lambda request: static("logo.png"),
    "SITE_SYMBOL": "work_history",

    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/svg+xml",
            "href": lambda request: static("logo.png"),
        },
    ],
    # Cấu hình chung
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True,
    "ENVIRONMENT": "development",
    "ENVIRONMENT_NAME": "Môi trường phát triển",
    "ENVIRONMENT_COLOR": "indigo",
    
    # Giao diện
    "BORDER_RADIUS": "12px",
    "COLOR_SCHEME": {
        "primary": {
            "50": "255 245 245",
            "100": "255 235 235",
            "200": "255 215 215",
            "300": "255 195 195",
            "400": "255 175 175",
            "500": "243 36 9",
            "600": "214 31 8",
            "700": "184 27 7",
            "800": "153 22 6",
            "900": "122 18 5",
            "950": "92 13 4",
        },
        "secondary": {
            "50": "240 240 255",
            "100": "224 224 255",
            "200": "192 192 255",
            "300": "160 160 255",
            "400": "128 128 255",
            "500": "0 0 102",
            "600": "0 0 68",
            "700": "0 0 34",
            "800": "0 0 17",
            "900": "0 0 8",
            "950": "0 0 4",
        },
    },
    "COLORS": {
        "primary": {
            "50": "255 245 245",
            "100": "255 235 235",
            "200": "255 215 215",
            "300": "255 195 195",
            "400": "255 175 175",
            "500": "243 36 9",
            "600": "214 31 8",
            "700": "184 27 7",
            "800": "153 22 6",
            "900": "122 18 5",
            "950": "92 13 4",
        },
        "secondary": {
            "50": "240 240 255",
            "100": "224 224 255",
            "200": "192 192 255",
            "300": "160 160 255",
            "400": "128 128 255",
            "500": "0 0 102",
            "600": "0 0 68",
            "700": "0 0 34",
            "800": "0 0 17",
            "900": "0 0 8",
            "950": "0 0 4",
        },
        "accent": {
            "50": "240 240 255",
            "100": "224 224 255",
            "200": "192 192 255",
            "300": "160 160 255",
            "400": "128 128 255",
            "500": "6 35 164",
            "600": "5 27 123",
            "700": "4 20 82",
            "800": "3 13 41",
            "900": "2 7 20",
            "950": "1 3 10",
        },
        "light": {
            "50": "240 240 255",
            "100": "224 224 255",
            "200": "192 192 255",
            "300": "160 160 255",
            "400": "128 128 255",
            "500": "0 68 255",
            "600": "0 51 204",
            "700": "0 34 153",
            "800": "0 17 102",
            "900": "0 8 51",
            "950": "0 4 25",
        },
        "background": {
            "50": "255 255 255",
            "100": "250 250 250",
            "200": "245 245 247",
            "300": "240 240 242",
            "400": "235 235 237",
            "500": "245 245 247",
            "600": "240 240 242",
            "700": "235 235 237",
            "800": "230 230 232",
            "900": "225 225 227",
            "950": "220 220 222",
        },
    },
    
    # Tùy chỉnh CSS và JS
    # "STYLES": [
    #     "https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&display=swap",
    #     lambda request: static("css/custom.css"),
    # ],
    

}