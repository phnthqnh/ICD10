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
from ICD10.models.chatbot import ChatMessage, ChatSession
from ICD10.models.feedback import Feedback_Chapter, Feedback_Block, Feedback_Disease, Feedback_Chatbot
from ICD10.serializers.feedback_serializers import FeedbackChapterSerializer, FeedbackBlockSerializer, FeedbackDiseaseSerializer, FeedbackChatbotSerializer
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

    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_feedback_chapter(request):
    """
    Gửi phản hồi về chương ICD-10
    """
    user = request.user
    data = request.data.copy()
    data['user'] = user.id  # Gán user hiện tại vào dữ liệu
    serializer = FeedbackChapterSerializer(data=data)
    if serializer.is_valid():
        # trường type_feedback gán bằng 1
        serializer.save(type_feedback=1)
        return AppResponse.success(
            SuccessCodes.SUBMIT_FEEDBACK_CHAPTER,
            data=serializer.data,
        )
    else:
        return AppResponse.error(
            ErrorCodes.INVALID_REQUEST,
            errors=serializer.errors,
        )
        
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_feedback_block(request):
    """
    Gửi phản hồi về nhóm ICD-10
    """
    user = request.user
    data = request.data.copy()
    data['user'] = user.id  # Gán user hiện tại vào dữ liệu
    serializer = FeedbackBlockSerializer(data=data)
    if serializer.is_valid():
        serializer.save(type_feedback=2)
        return AppResponse.success(
            SuccessCodes.SUBMIT_FEEDBACK_BLOCK,
            data=serializer.data,
        )
    else:
        return AppResponse.error(
            ErrorCodes.INVALID_REQUEST,
            errors=serializer.errors,
        )
        
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_feedback_disease(request):
    """
    Gửi phản hồi về mã bệnh ICD-10
    """
    user = request.user
    data = request.data.copy()
    data['user'] = user.id  # Gán user hiện tại vào dữ liệu
    serializer = FeedbackDiseaseSerializer(data=data)
    if serializer.is_valid():
        serializer.save(type_feedback=3)
        return AppResponse.success(
            SuccessCodes.SUBMIT_FEEDBACK_DISEASE,
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
    data.pop("user", None)   # XÓA user gửi từ client nếu có
    # Nếu user không bằng feedback.chat_message.session.user thì lỗi
    chat_message_id = data.get('chat_message')
    chat_message = ChatMessage.objects.filter(id=chat_message_id).first()
    if not chat_message:
        return AppResponse.error(
            ErrorCodes.INVALID_REQUEST,
            errors="Tin nhắn không tồn tại",
        )
    if chat_message.session.user != user:
        return AppResponse.error(
            ErrorCodes.INVALID_REQUEST,
            errors="Bạn không có quyền gửi phản hồi cho tin nhắn này",
        )
    # data['chat_message'] = chat_message.id  # Gán chat_message vào dữ liệu

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
        

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_feedbacks_icd_by_user(request):
    """
    Lấy phản hồi icd10 của user trong feedback_chapter, feedback_block, feedback_disease
    """
    user = request.user
    feedbacks_chapter = Feedback_Chapter.objects.filter(user=user).order_by("-created_at")
    feedbacks_block = Feedback_Block.objects.filter(user=user).order_by("-created_at")
    feedbacks_disease = Feedback_Disease.objects.filter(user=user).order_by("-created_at")
    serializer_chapter = FeedbackChapterSerializer(feedbacks_chapter, many=True)
    serializer_block = FeedbackBlockSerializer(feedbacks_block, many=True)
    serializer_disease = FeedbackDiseaseSerializer(feedbacks_disease, many=True)
    return AppResponse.success(
        SuccessCodes.GET_USER_FEEDBACKS_ICD10,
        data={
            "chapter_feedbacks": serializer_chapter.data,
            "block_feedbacks": serializer_block.data,
            "disease_feedbacks": serializer_disease.data,
        },
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