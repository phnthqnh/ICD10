from asyncio.log import logger
import hashlib
from django.utils import timezone
import os
from django.conf import settings
import pytz
import importlib
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
import re
from django.contrib.contenttypes.models import ContentType
import logging
from constants.error_codes import ErrorCodes
import difflib
from ICD10.models.chatbot import ChatMessage, ChatSession
import requests
from constants.constants import Constants
from libs.Redis import RedisWrapper
from libs.response_handle import AppResponse
import os
import boto3, uuid
from django.core import signing, mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from ICD10.models.icd10 import ICDDisease, DiseaseExtraInfo


class Utils:
    # khởi tạo model một lần duy nhất khi import Utils
    _model = None
    
    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls._model = SentenceTransformer("intfloat/multilingual-e5-base")
        return cls._model
    
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
            # Upload file lên S3 (private, mặc định không ACL)
            s3.upload_fileobj(
                file_obj,
                os.getenv("AWS_STORAGE_BUCKET_NAME"),
                file_name,
            )
        except Exception as e:
            return AppResponse.error(ErrorCodes.INTERNAL_SERVER_ERROR, errors=str(e))

        # Tạo presigned URL (ví dụ sống 1h = 3600s)
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': os.getenv("AWS_STORAGE_BUCKET_NAME"),
                'Key': file_name
            },
            ExpiresIn=3600
        )
        
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
    def add_new_disease_embedding(disease_code):
        """
        Thêm embedding cho bệnh mới (nếu chưa tồn tại trong FAISS index).
        """
        try:
            index = faiss.read_index("icd10_index_vi.faiss")
            texts = np.load("icd10_texts_vi.npy", allow_pickle=True)
            codes = np.load("icd10_codes.npy", allow_pickle=True)

            if disease_code in codes:
                print(f"⚠️ Mã bệnh {disease_code} đã tồn tại trong index, dùng reembed_disease thay vì thêm mới.")
                return

            # --- Lấy dữ liệu mới từ DB ---
            try:
                d = ICDDisease.objects.get(code=disease_code)
            except ICDDisease.DoesNotExist:
                print(f"❌ Không tìm thấy mã bệnh {disease_code} trong database.")
                return

            extra_info = DiseaseExtraInfo.objects.filter(disease=d).first()
            if extra_info:
                new_text = f"{d.code} - {d.title_vi} - {extra_info.description or ''} - {extra_info.symptoms or ''}"
            else:
                new_text = f"{d.code} - {d.title_vi}"

            # --- Encode text mới ---
            model = Utils.get_model()
            new_vector = model.encode(
                [f"query: {new_text}"],
                convert_to_numpy=True,
                normalize_embeddings=True
            )

            # --- Thêm vào FAISS ---
            index.add(new_vector)

            # --- Append vào danh sách ---
            texts = np.append(texts, new_text)
            codes = np.append(codes, disease_code)

            # --- Ghi lại ---
            faiss.write_index(index, "icd10_index_vi.faiss")
            np.save("icd10_texts_vi.npy", texts)
            np.save("icd10_codes.npy", codes)

            print(f"✅ Đã thêm embedding cho bệnh mới {disease_code}.")
            
            return True
        except Exception as e:
            Utils.logger().error(f"Lỗi khi thêm embedding cho bệnh mới {disease_code}: {e}")
            raise

    @staticmethod
    def reembed_disease(disease_code):
        """
        Cập nhật lại embedding cho 1 bệnh cụ thể trong FAISS + file .npy
        """
        try:    
            # --- Bước 1: Load dữ liệu gốc ---
            index = faiss.read_index("icd10_index_vi.faiss")
            texts = np.load("icd10_texts_vi.npy", allow_pickle=True)
            codes = np.load("icd10_codes.npy", allow_pickle=True)

            if disease_code not in codes:
                print(f"⚠️ Không tìm thấy mã bệnh {disease_code} trong danh sách codes.")
                return

            # --- Bước 2: Lấy dữ liệu mới từ DB ---
            d = ICDDisease.objects.get(code=disease_code)
            extra_info = DiseaseExtraInfo.objects.filter(disease=d).first()
            if extra_info:
                new_text = f"{d.code} - {d.title_vi} - {extra_info.description or ''} - {extra_info.symptoms or ''}"
            else:
                new_text = f"{d.code} - {d.title_vi}"

            # --- Bước 3: Encode lại ---
            model = Utils.get_model()
            new_vector = model.encode(
                [f"query: {new_text}"],
                convert_to_numpy=True,
                normalize_embeddings=True
            )[0]

            # --- Bước 4: Cập nhật vào FAISS ---
            idx = np.where(codes == disease_code)[0][0]  # vị trí trong mảng

            # Lấy tất cả vectors từ index hiện tại
            vectors = np.zeros((index.ntotal, index.d), dtype="float32")
            for i in range(index.ntotal):
                vectors[i] = index.reconstruct(i)
                
            # Cập nhật vector mới vào vị trí tương ứng
            vectors[idx] = new_vector
            # Tạo index mới và thêm tất cả vectors vào
            new_index = faiss.IndexFlatIP(vectors.shape[1])
            new_index.add(vectors)

            # --- Bước 5: Ghi lại dữ liệu ---
            texts[idx] = new_text
            faiss.write_index(new_index, "icd10_index_vi.faiss")
            np.save("icd10_texts_vi.npy", texts)
            print(f"✅ Đã re-embed thành công bệnh {disease_code}.")
            
            return True
        except Exception as e:
            Utils.logger().error(f"Lỗi khi re-embed bệnh {disease_code}: {e}")
            raise
