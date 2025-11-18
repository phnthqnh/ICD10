import os, random
import boto3, uuid
from rest_framework.permissions import AllowAny,IsAuthenticated
from constants.constants import Constants
from configuration.jwt_config import JwtConfig
from libs.response_handle import AppResponse
from constants.error_codes import ErrorCodes
from constants.success_codes import SuccessCodes
from django.http import HttpResponseRedirect
from django.core import signing
from constants.redis_keys import Rediskeys
from ICD10.models.user import User
from ICD10.serializers.user_serializers import UserSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
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
from django.views.decorators.cache import cache_page
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

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

@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def verify_email(request):
    token = request.GET.get("token")
    if not token:
        return AppResponse.error(ErrorCodes.TOKEN_REQUIRED)
    try:
        data = signing.loads(token, salt="email-verify", max_age=60*2)  # 2 minutes
        user = User.objects.get(id=data["user_id"], email=data["email"])
        user.email_verified = True
        user.status = 1  # Active
        user.save()

        # Redirect về trang thông báo thành công
        return HttpResponseRedirect("http://localhost:4200/sign-in")
    except signing.BadSignature:
        # Redirect về trang thông báo lỗi
        return HttpResponseRedirect("http://localhost:4200/not-verify-email")


@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def user_register(request):
    email = request.data.get("email")
    existing_user = User.objects.filter(email=email).first()
    # 🔁 Nếu người dùng đã tồn tại nhưng chưa kích hoạt
    if existing_user and existing_user.status == 3:
        token = Utils.generate_verification_token(existing_user)
        activation_url = os.getenv("activation_url")
        activation_link = f"{activation_url}?token={token}"

        Utils.send_activation_email(
            user=existing_user,
            activation_link=activation_link
        )

        return AppResponse.success(
            SuccessCodes.RESEND_VERIFICATION,
            data={"email": email, "message": "Email kích hoạt mới đã được gửi."}
        )
    
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
        token = Utils.generate_verification_token(user)
        activation_url = os.getenv("activation_url")
        activation_link = f"{activation_url}?token={token}"
        # Gửi email
        Utils.send_activation_email(
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
def verified_doctor(request):
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return AppResponse.error(ErrorCodes.USER_NOT_FOUND)

    file_obj = request.FILES.get("file")
    if not file_obj:
        return AppResponse.error(ErrorCodes.VALIDATION_ERROR, errors="File is required")

    file_name, presigned_url = Utils.save_file_to_s3(file_obj, "verification")
    if not file_name or not presigned_url:
        return AppResponse.error(ErrorCodes.INTERNAL_SERVER_ERROR, errors="Failed to upload file")
    
    # Lưu key file vào DB (không nên lưu presigned URL vì hết hạn)
    user.verification_file = file_name
    user.role = 1  # Doctor role
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data["refresh_token"]
        token = RefreshToken(refresh_token)
        token.blacklist()

        return AppResponse.success(SuccessCodes.LOGOUT)
    except KeyError:
        return AppResponse.error(ErrorCodes.REFRESH_TOKEN_REQUIRED)
    except Exception as e:
        return AppResponse.error(ErrorCodes.INTERNAL_SERVER_ERROR, errors=str(e))



@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def request_password_reset(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return AppResponse.error(ErrorCodes.VALIDATION_ERROR, errors=serializer.errors)

    email = serializer.validated_data['email']
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return AppResponse.error(ErrorCodes.USER_NOT_FOUND)

    # --- Sinh mã OTP 6 chữ số ---
    otp = str(random.randint(100000, 999999))

    # --- Lưu OTP vào cache (hoặc Redis) trong 5 phút ---
    cache_key = f"password_reset_otp_{email}"
    RedisWrapper.save(cache_key, otp, expire_time=5 * 60)  # 5 phút

    # --- Gửi email ---
    Utils.email_reset_password(user=user, otp=otp)

    return AppResponse.success(SuccessCodes.PASSWORD_RESET_EMAIL_SENT)



@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def reset_password_confirm(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if not serializer.is_valid():
        return AppResponse.error(ErrorCodes.VALIDATION_ERROR, errors=serializer.errors)

    email = serializer.validated_data['email']
    otp = serializer.validated_data['otp']
    new_password = serializer.validated_data['new_password']

    # --- Kiểm tra mã OTP ---
    cache_key = f"password_reset_otp_{email}"
    saved_otp = RedisWrapper.get(cache_key)
    print("saved_otp", saved_otp)
    if not saved_otp:
        return AppResponse.error(ErrorCodes.OTP_EXPIRED, errors="OTP đã hết hạn hoặc không tồn tại.")

    if str(otp).strip() != str(saved_otp).strip():
        return AppResponse.error(ErrorCodes.OTP_INVALID, errors="Mã OTP không chính xác.")

    # --- Cập nhật mật khẩu ---
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return AppResponse.error(ErrorCodes.USER_NOT_FOUND)

    user.set_password(new_password)
    user.save()

    # --- Xóa OTP khỏi cache ---
    RedisWrapper.remove(cache_key)

    return AppResponse.success(SuccessCodes.PASSWORD_RESET_SUCCESS)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    return AppResponse.success(SuccessCodes.GET_USER_PROFILE, data=UserSerializer(request.user).data)