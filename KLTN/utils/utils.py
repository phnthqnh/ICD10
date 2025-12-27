from asyncio.log import logger
import hashlib
from django.utils import timezone
import os
from django.conf import settings
import pytz
import importlib
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
import logging
from constants.error_codes import ErrorCodes
from ICD10.models.chatbot import ChatMessage
import requests
from constants.constants import Constants
from libs.Redis import RedisWrapper
from libs.response_handle import AppResponse
import os
import boto3, uuid
from django.core import signing
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
from ICD10.models.login_event import LoginEvent


class Utils:
    
    @staticmethod
    def get_token_from_header(request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]
        return None

    @staticmethod
    def hash_lib_sha(val):
        return hashlib.sha256(val.encode()).hexdigest()

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")

    @staticmethod
    def get_current_datetime():
        vie_tz = pytz.timezone("Asia/Ho_Chi_Minh")
        return timezone.now().astimezone(vie_tz)

    @staticmethod
    def validate_uidb64(uidb64):
        return force_str(urlsafe_base64_decode(uidb64))

    @staticmethod
    def get_setting(key, default=None, cast_type=None):
        value = getattr(settings, key, os.getenv(key, default))
        if value in [None, ""]:
            return default
        if cast_type:
            try:
                return cast_type(value)
            except (ValueError, TypeError):
                return default
        return value

    # Logging utils
    @staticmethod
    def get_class_with_importlib(module_path: str, wanted_class: str):
        module = importlib.import_module(module_path)
        return getattr(module, wanted_class)

    @staticmethod
    def logger():
        return logging.getLogger(__name__)

    @staticmethod
    def serialize_queryset_chapter(queryset, fields=None):
        """
        Chuyển queryset hoặc list object thành list dict chỉ chứa các field cần thiết.
        Mặc định: ["code", "title_en", "title_vi"]
        """
        if fields is None:
            fields = ["id", "chapter", "code", "title_en", "title_vi"]

        data = []
        for obj in queryset:
            item = {}
            for field in fields:
                # getattr để lấy từ object (model instance)
                # nếu dùng .values() thì không cần getattr
                item[field] = getattr(obj, field, None)
            data.append(item)
        return data
    @staticmethod
    def serialize_queryset(queryset, fields=None):
        """
        Chuyển queryset hoặc list object thành list dict chỉ chứa các field cần thiết.
        Mặc định: ["code", "title_en", "title_vi"]
        """
        if fields is None:
            fields = ["id", "code", "title_en", "title_vi"]

        data = []
        for obj in queryset:
            item = {}
            for field in fields:
                # getattr để lấy từ object (model instance)
                # nếu dùng .values() thì không cần getattr
                item[field] = getattr(obj, field, None)
            data.append(item)
        return data
    
    @staticmethod
    def serialize_extrainfo_queryset(queryset, fields=None):
        """
        Chuyển queryset hoặc list object thành list dict chỉ chứa các field cần thiết.
        Mặc định: ["code", "title_en", "title_vi"]
        """
        if fields is None:
            fields = ["id", "code", "title_en", "title_vi", "description", "symptoms", "image_url", "wikipedia_url"]

        data = []
        for obj in queryset:
            item = {}
            for field in fields:
                # getattr để lấy từ object (model instance)
                # nếu dùng .values() thì không cần getattr
                item[field] = getattr(obj, field, None)
            data.append(item)
        return data
    
    @staticmethod
    def _generate_chat_summary(session, api_key):
        messages = ChatMessage.objects.filter(session=session).order_by("created_at")
        full_text = "\n".join([f"{m.role}: {m.content}" for m in messages])

        prompt = Constants.PROMPT_AI_SUMMARY.replace("{full_text}", full_text)

        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        url = f"{Constants.GEMINI_API_URL}?key={api_key}"

        try:
            res = requests.post(url, headers=headers, json=payload, timeout=15)
            res.raise_for_status()
            data = res.json()
            summary_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if summary_text:
                key = f"chat_summary_{session.id}"
                RedisWrapper.save(key, summary_text, expire_time=60 * 60 * 24 * 60)  # 2 tháng
                print(f"✅ Saved summary to Redis for session {session.id}")
        except Exception as e:
            logger.error(f"Lỗi khi tạo summary: {e}")
            
    @staticmethod
    def save_file_to_s3(file_obj, folder):
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_S3_REGION_NAME"),
        )

        file_name = f"{folder}/{uuid.uuid4()}_{file_obj.name}"
        try:
            file_obj.seek(0)
            content_type = file_obj.content_type if hasattr(file_obj, "content_type") else "application/octet-stream"

            # Upload file lên S3 (private, mặc định không ACL)
            s3.upload_fileobj(
                file_obj,
                os.getenv("AWS_STORAGE_BUCKET_NAME"),
                file_name,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': content_type
                }
            )
        except Exception as e:
            return AppResponse.error(ErrorCodes.INTERNAL_SERVER_ERROR, errors=str(e))

        # Tạo presigned URL cho file
        # presigned_url = s3.generate_presigned_url(
        #     'get_object',
        #     Params={
        #         'Bucket': os.getenv("AWS_STORAGE_BUCKET_NAME"),
        #         'Key': file_name
        #     }
        # )
        
        presigned_url = f"https://{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.ap-southeast-2.amazonaws.com/{file_name}"
        
        return file_name, presigned_url
    
    @staticmethod
    def generate_verification_token(user):
        data = {"user_id": user.id, "email": user.email}
        return signing.dumps(data, salt="email-verify")

    @staticmethod
    def send_activation_email(user, activation_link):
        subject = "Kích hoạt tài khoản ICD10"
        from_email = "noreply@icd10.com"
        to = [user.email]

        html_content = render_to_string('email_template.html', {'username': user.username,
                                                            'activation_link': activation_link})
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")

        # attach logo
        with open("templates/logo/logo.png", "rb") as f:  # nên dùng png thay vì svg
            logo = MIMEImage(f.read(), _subtype="png")
            logo.add_header('Content-ID', '<logo_image>')
            logo.add_header('Content-Disposition', 'inline', filename="logo.png")
            msg.attach(logo)

        msg.send()
        
        
    @staticmethod
    def verify_change_email(user, activation_link):
        subject = "Xác minh email mới trong ICD10"
        from_email = "noreply@icd10.com"
        to = [user.pending_email]

        html_content = render_to_string('verify_email_template.html', {'username': user.username,
                                                            'activation_link': activation_link})
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")

        # attach logo
        with open("templates/logo/logo.png", "rb") as f:  # nên dùng png thay vì svg
            logo = MIMEImage(f.read(), _subtype="png")
            logo.add_header('Content-ID', '<logo_image>')
            logo.add_header('Content-Disposition', 'inline', filename="logo.png")
            msg.attach(logo)

        msg.send()
        
    @staticmethod
    def email_reset_password(user, otp):
        subject = "Đặt lại mật khẩu ICD10"
        from_email = "noreply@icd10.com"
        to = [user.email]
        
        html_content = render_to_string('reset_password_email_template.html', {'username': user.username,
                                                            'otp': otp})
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        
        # attach logo
        with open("templates/logo/logo.png", "rb") as f:  # nên dùng png thay vì svg
            logo = MIMEImage(f.read(), _subtype="png")
            logo.add_header('Content-ID', '<logo_image>')
            logo.add_header('Content-Disposition', 'inline', filename="logo.png")
            msg.attach(logo)

        msg.send()
        
    @staticmethod
    def admin_send_activation_email(user, password, activation_link):
        subject = "Kích hoạt tài khoản ICD10"
        from_email = "noreply@icd10.com"
        to = [user.email]

        html_content = render_to_string('admin_email_template.html', {'username': user.username,
                                                            'activation_link': activation_link,
                                                            'password': password})
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")

        # attach logo
        with open("templates/logo/logo.png", "rb") as f:  # nên dùng png thay vì svg
            logo = MIMEImage(f.read(), _subtype="png")
            logo.add_header('Content-ID', '<logo_image>')
            logo.add_header('Content-Disposition', 'inline', filename="logo.png")
            msg.attach(logo)

        msg.send()
        
    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")
    
    @staticmethod
    def log_login_event(request, *, user=None, status, identifier=None):
        ip_address = Utils.get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        device = request.META.get("HTTP_DEVICE", "")

        LoginEvent.objects.create(
            user=user,
            status=status,
            ip_adress=ip_address,
            user_agent=user_agent,
            device=device,
            identifier=identifier
        )