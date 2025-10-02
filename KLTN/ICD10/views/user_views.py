import os
import boto3, uuid
from rest_framework.permissions import AllowAny,IsAuthenticated
from constants.constants import Constants
from configuration.jwt_config import JwtConfig
from libs.response_handle import AppResponse
from constants.error_codes import ErrorCodes
from constants.success_codes import SuccessCodes
from django.http import HttpResponseRedirect
from django.core import signing, mail
from constants.redis_keys import Rediskeys
from ICD10.models.user import User
from  ICD10.serializers.user_serializers import UserSerializer
from utils.utils import Utils
from permissions.permisstions import IsAdmin
from libs.Redis import RedisWrapper
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from constants.error_codes import ErrorCodes
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
from django.views.decorators.cache import cache_page
# # TEST
# import pandas as pd
# from datetime import date
# from datetime import datetime
# from django.conf import settings
# import os


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get("email", "").strip()
    username = request.data.get("username", "").strip()
    password = request.data.get("password")
    
    if (not email and not username) or not password:
        return AppResponse.error(ErrorCodes.EMAIL_OR_USERNAME_REQUIRED)

    user = None
    if email:
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            pass

    if not user and username:
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            pass

    if email and username and user:
        if (
            user.email.lower() != email.lower()
            and user.username.lower() != username.lower()
        ):
            return AppResponse.error(ErrorCodes.INCORRECT_UE_OR_PASSWORD)

    if not user:
        return AppResponse.error(ErrorCodes.USER_NOT_FOUND)
    identifier = str(user.id)
    if not user.is_superuser:
        block_key = Rediskeys.LOGIN_BLOCK(identifier)
        if RedisWrapper.get(block_key):
            return AppResponse.error(
                ErrorCodes.LOGIN_TOO_MANY_ATTEMPTS,
                remaining_time=get_user_block_time(block_key),
            )

    attempt_key = Rediskeys.LOGIN_ATTEMPT(identifier) if not user.is_superuser else None

    if not user.password or not user.check_password(password):
        if not user.is_superuser:
            attempts = int(RedisWrapper.get(attempt_key) or 0) + 1
            RedisWrapper.save(
                attempt_key, attempts, expire_time=Constants.ATTEMPT_BLOCK_USER
            )
            if attempts >= 5:
                RedisWrapper.save(block_key, True, Constants.ATTEMPT_BLOCK_USER)
                RedisWrapper.remove(attempt_key)
                return AppResponse.error(
                    ErrorCodes.LOGIN_TOO_MANY_ATTEMPTS,
                    remaining_time=get_user_block_time(block_key),
                )

            return AppResponse.error(
                ErrorCodes.INCORRECT_UE_OR_PASSWORD, errors=f"{5 - attempts}"
            )
        else:
            return AppResponse.error(ErrorCodes.INCORRECT_UE_OR_PASSWORD)

    if not user.is_superuser and user.status in [2, 3]:
        return AppResponse.error(ErrorCodes.USER_INACTIVE, user_status=user.status)

    if not user.is_superuser:
        RedisWrapper.remove(attempt_key)
        RedisWrapper.remove(block_key)

    user.last_login = Utils.get_current_datetime()
    
    user.save()
    user_data = save_user(user)
   
    return AppResponse.success(
        SuccessCodes.LOGIN,
        data={
            "user": UserSerializer(user).data,
          
            "token": user_data["token"],
            "refresh_token": user_data["refresh_token"],
        },
    )


def get_user_block_time(key):
    time = RedisWrapper.ttl(key)
    return f"{time // 60}:{time % 60}" if time else None


def generate_verification_token(user):
    data = {"user_id": user.id, "email": user.email}
    return signing.dumps(data, salt="email-verify")

@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def verify_email(request):
    token = request.GET.get("token")
    if not token:
        return AppResponse.error(ErrorCodes.TOKEN_REQUIRED)
    try:
        data = signing.loads(token, salt="email-verify", max_age=60*2)  # 5 minutes
        user = User.objects.get(id=data["user_id"], email=data["email"])
        user.email_verified = True
        user.status = 1  # Active
        user.save()

        # Redirect về trang thông báo thành công
        return HttpResponseRedirect("http://localhost:8000/admin/login")
    except signing.BadSignature:
        # Redirect về trang thông báo lỗi
        return HttpResponseRedirect("http://localhost:8000/admin/login")
    
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

@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def user_register(request):
    
    serializer = UserSerializer(
        data=request.data,
        context={
            "request": request,
            Constants.USER_REGISTER: True,
        },
    )
    if not serializer.is_valid():
        return AppResponse.error(ErrorCodes.VALIDATION_ERROR, errors=serializer.errors)

    try:
        user = serializer.save()
        user.status = 3  # Waiting for email verification
        user.save()

        # Tạo token
        token = generate_verification_token(user)
        activation_url = os.getenv("activation_url")
        activation_link = f"{activation_url}?token={token}"
        # Gửi email
        send_activation_email(
            user=user,
            activation_link=activation_link
        )
        return AppResponse.success(SuccessCodes.REGISTER, data=UserSerializer(user).data)
    except Exception as e:
        return AppResponse.error(ErrorCodes.INTERNAL_SERVER_ERROR, errors=str(e))


def save_user(user):
    tr = JwtConfig.generate(user)
  
    
    redis_user_data = {
        "user": UserSerializer(user).data,
      
    }
   
    is_save = RedisWrapper.save(tr["redis_key"], redis_user_data)

    return {
        "user": user,
     
       
        "token": tr["token"],
        "refresh_token": tr["refresh_token"],
        "is_save": is_save,
    }

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    try:
        new_password:str = request.data.get('new_password')

        if not new_password:
            return AppResponse.error(error_code=ErrorCodes.NEW_PASSWORD_REQUIRED,e="Password is required")
    

        try:
            validate_password(new_password,request.user)

        except ValidationError as e:
            return AppResponse.error(error_code=ErrorCodes.VALIDATION_NEW_PASSWORD)

        with transaction.atomic():
            user:User = request.user
            user.password = user.set_password(new_password)
            user.save()

        return AppResponse.success(success_code=SuccessCodes.CHANGE_PASSWORD)
    except Exception as e:
        return AppResponse.error(error_code=ErrorCodes.CANNOT_CHANGE_PASSWORD,errors=str(e))

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def verified_doctor(request, pk):
    try:
        user = User.objects.get(id=pk)
        if request.user.id != user.id:
            return AppResponse.error(ErrorCodes.PERMISSION_DENIED)
    except User.DoesNotExist:
        return AppResponse.error(ErrorCodes.USER_NOT_FOUND)

    file_obj = request.FILES.get("file")
    if not file_obj:
        return AppResponse.error(ErrorCodes.VALIDATION_ERROR, errors="File is required")

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_S3_REGION_NAME"),
    )

    file_name = f"verification/{uuid.uuid4()}_{file_obj.name}"
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

    # Lưu key file vào DB (không nên lưu presigned URL vì hết hạn)
    user.verification_file = file_name
    user.is_verified_doctor = False  # chờ admin xác thực

    serializer = UserSerializer(
        user, 
        data=request.data,
        partial=True,
        context={
            "request": request,
            Constants.EDIT_USER_PROFILE: True,
        },
    )
    if serializer.is_valid():
        updated_user = serializer.save()
        return AppResponse.success(
            SuccessCodes.UPDATE_USER_PROFILE, 
            data={
                "user": UserSerializer(updated_user).data,
                "verification_file_url": presigned_url  # client lấy link tạm thời
            }
        )
    return AppResponse.error(ErrorCodes.VALIDATION_ERROR, errors=serializer.errors)

@api_view(["GET"])
@permission_classes([IsAdmin])
def get_users_waiting_verification(request):
    # 1. Lấy dữ liệu từ cache
    cached_users = RedisWrapper.get(Constants.CACHE_KEY_WAITING_USERS)
    if cached_users:
        return AppResponse.success(
            SuccessCodes.LIST_VERIFICATION,
            data=cached_users
        )
    # 2. Nếu chưa có cache -> query DB
    users = User.objects.filter(is_verified_doctor=False, verification_file__isnull=False)
    serialized_users = UserSerializer(users, many=True).data
    # 3. Lưu vào cache (ví dụ 15 phút)
    RedisWrapper.save(Constants.CACHE_KEY_WAITING_USERS, serialized_users, expire_time=60*15)
    
    return AppResponse.success(
        SuccessCodes.LIST_VERIFICATION,
        data=serialized_users
    )


@api_view(["PUT"])
@permission_classes([IsAdmin])
def approve_doctor_verification(request, pk):
    try:
        user = User.objects.get(id=pk)
    except User.DoesNotExist:
        return AppResponse.error(ErrorCodes.USER_NOT_FOUND)
    # phai co file verification moi duoc phep xet
    if not user.verification_file:
        return AppResponse.error(ErrorCodes.NOT_HAVE_VERIFICATION_FILE)
    
    user.is_verified_doctor = True
    user.role = 2  # Doctor role
    user.save()

    # Xoá cache để đảm bảo lần GET tiếp theo lấy data mới
    RedisWrapper.remove(Constants.CACHE_KEY_WAITING_USERS)

    return AppResponse.success(SuccessCodes.VERIFIED_DOCTOR, data=UserSerializer(user).data)