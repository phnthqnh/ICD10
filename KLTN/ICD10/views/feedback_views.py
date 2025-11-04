import os
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
from ICD10.models.icd10 import ICDDisease, DiseaseExtraInfo
from ICD10.models.feedback import Feedback_ICD10, Feedback_Chatbot
from ICD10.serializers.feedback_serializers import FeedbackICD10Serializer, FeedbackChatbotSerializer
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


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def get_all_feedbacks_icd(request):
    """
    Lấy tất cả feedback icd10
    """
    feedbacks = Feedback_ICD10.objects.all().order_by("-created_at")
    serializer = FeedbackICD10Serializer(feedbacks, many=True)
    return AppResponse.success(
        SuccessCodes.GET_FEEDBACKS_ICD10,
        data=serializer.data,
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def get_all_feedbacks_chatbot(request):
    """
    Lấy tất cả feedback chatbot
    """
    feedbacks = Feedback_Chatbot.objects.all().order_by("-created_at")
    serializer = FeedbackChatbotSerializer(feedbacks, many=True)
    return AppResponse.success(
        SuccessCodes.GET_FEEDBACKS_CHATBOT,
        data=serializer.data,
    )
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_feedback_icd(request):
    """
    Gửi phản hồi về mã bệnh ICD-10
    """
    user = request.user
    data = request.data.copy()
    data['user'] = user.id  # Gán user hiện tại vào dữ liệu

    # disease = ICDDisease.objects.filter(id=pk).first()
    # if not disease:
    #     return AppResponse.error(
    #         ErrorCodes.INVALID_REQUEST,
    #         errors="Mã bệnh không tồn tại",
    #     )
    # data['disease'] = disease.id
    serializer = FeedbackICD10Serializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return AppResponse.success(
            SuccessCodes.SUBMIT_FEEDBACK_ICD10,
            data=serializer.data,
        )
    else:
        return AppResponse.error(
            ErrorCodes.INVALID_REQUEST,
            errors=serializer.errors,
        )
        
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_feedback_chatbot(request):
    """
    Gửi phản hồi về chatbot
    """
    user = request.user
    data = request.data.copy()
    data['user'] = user.id  # Gán user hiện tại vào dữ liệu

    serializer = FeedbackChatbotSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return AppResponse.success(
            SuccessCodes.SUBMIT_FEEDBACK_CHATBOT,
            data=serializer.data,
        )
    else:
        return AppResponse.error(
            ErrorCodes.INVALID_REQUEST,
            errors=serializer.errors,
        )
        
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def accept_feedback_icd(request, pk):
    """
    Chấp nhận phản hồi về icd10 (cập nhật trạng thái sau khi đã xử lý)
    """
    try:
        feedback = Feedback_ICD10.objects.get(id=pk)
        description = feedback.description
        symptoms = feedback.symptoms
        image = feedback.image
        disease = feedback.disease
        disease_extra = DiseaseExtraInfo.objects.filter(disease=disease).first()
        # Cập nhật thông tin bệnh theo phản hồi
        if disease_extra:
            if description:
                disease_extra.description = description
            if symptoms:
                disease_extra.symptoms = symptoms
            if image:
                disease_extra.image = image
            disease_extra.save()
            
        feedback.status = 1  # Accepted
        feedback.save()
        return AppResponse.success(
            SuccessCodes.ACCEPT_FEEDBACK_ICD10,
            data={},
        )
    except Feedback_ICD10.DoesNotExist:
        return AppResponse.error(
            ErrorCodes.INVALID_REQUEST,
            errors="Phản hồi không tồn tại",
        )
        
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def accept_feedback_chatbot(request, pk):
    """
    Chấp nhận phản hồi về chatbot (cập nhật trạng thái sau khi đã xử lý)
    """
    try:
        feedback = Feedback_Chatbot.objects.get(id=pk)
            
        feedback.status = 1  # Accepted
        feedback.save()
        return AppResponse.success(
            SuccessCodes.ACCEPT_FEEDBACK_CHATBOT,
            data={},
        )
    except Feedback_Chatbot.DoesNotExist:
        return AppResponse.error(
            ErrorCodes.INVALID_REQUEST,
            errors="Phản hồi không tồn tại",
        )
        
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def reject_feedback_icd(request, pk):
    """
    Từ chối phản hồi về icd10 (cập nhật trạng thái sau khi đã xử lý)
    """
    try:
        feedback = Feedback_ICD10.objects.get(id=pk)
        feedback.status = 2  # Rejected
        feedback.save()
        return AppResponse.success(
            SuccessCodes.REJECT_FEEDBACK_ICD10,
            data={},
        )
    except Feedback_ICD10.DoesNotExist:
        return AppResponse.error(
            ErrorCodes.INVALID_REQUEST,
            errors="Phản hồi không tồn tại",
        )
        
        
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def reject_feedback_chatbot(request, pk):
    """
    Từ chối phản hồi về chatbot (cập nhật trạng thái sau khi đã xử lý)
    """
    try:
        feedback = Feedback_Chatbot.objects.get(id=pk)
        feedback.status = 2  # Rejected
        feedback.save()
        return AppResponse.success(
            SuccessCodes.REJECT_FEEDBACK_CHATBOT,
            data={},
        )
    except Feedback_Chatbot.DoesNotExist:
        return AppResponse.error(
            ErrorCodes.INVALID_REQUEST,
            errors="Phản hồi không tồn tại",
        )
        
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_feedbacks_icd_by_user(request):
    """
    Lấy phản hồi icd10 của user hiện tại
    """
    user = request.user
    feedbacks = Feedback_ICD10.objects.filter(user=user).order_by("-created_at")
    serializer = FeedbackICD10Serializer(feedbacks, many=True)
    return AppResponse.success(
        SuccessCodes.GET_USER_FEEDBACKS_ICD10,
        data=serializer.data,
    )
    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_feedbacks_chatbot_by_user(request):
    """
    Lấy phản hồi chatbot của user hiện tại
    """
    user = request.user
    feedbacks = Feedback_Chatbot.objects.filter(user=user).order_by("-created_at")
    serializer = FeedbackChatbotSerializer(feedbacks, many=True)
    return AppResponse.success(
        SuccessCodes.GET_USER_FEEDBACKS_CHATBOT,
        data=serializer.data,
    )