from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from ICD10.serializers.icd10_serializers import *
from ICD10.models.icd10 import *
from ICD10.models.chatbot import *
from constants.constants import Constants
from libs.response_handle import AppResponse
from libs.Redis import RedisWrapper
from permissions.permisstions import IsAdmin, IsUser
from constants.error_codes import ErrorCodes
from constants.success_codes import SuccessCodes
from utils.utils import Utils
from ICD10.models.user import User
from django.views.decorators.cache import cache_page
from ICD10.ws_stream import stream_to_ws
import os
import requests
import time
import json
import logging
import uuid
import base64
from django.urls import reverse
from django.conf import settings
from ICD10.services.chat_services import GeminiChatService
from django.db import transaction
from icd10_agent.agent import root_agent
from ICD10.serializers.chatbot_serializers import ChatSessionSerializer, ChatMessageSerializer
from ICD10.models.user import User

# Khởi tạo logger
logger = logging.getLogger(__name__)

from google.genai import types
import asyncio
from asgiref.sync import sync_to_async, async_to_sync
from icd10_agent.runner import AGENT_RUNNER, SESSION_SERVICE

async def create_session(app_name, user_id):
    return await SESSION_SERVICE.create_session(
        app_name=app_name,
        user_id=user_id,
        state= {"initial_key": "initial_value"}
    )
    
    
@api_view(['POST']) 
@permission_classes([IsAuthenticated]) 
@transaction.atomic 
def chat_with_ai(request): 
    """ 
    - Nhận text và/hoặc image 
    - Tự detect intent nhờ ROOT_PROMPTS 
    - Agent tự gọi tool thích hợp 
    """ 
    user = request.user 
    text_query = request.data.get("text", "").strip() 
    image_file = request.FILES.get("image", None) 
    session_id = request.data.get("session_id") 
    
    if not text_query and not image_file: 
        return Response({"error": "Vui lòng nhập tin nhắn hoặc tải ảnh."}, status=400) 
    
    if len(text_query) > 50: 
        title = text_query[:50] 
    else: 
        title = text_query 
    
    if session_id: 
        session = ChatSession.objects.filter(id=session_id, user=user).first() 
        if not session: 
            return Response({"error": "Session không tồn tại"}, status=400) 
    else: 
        session = ChatSession.objects.create(user=user, title=title) 
        
    user_image = None 
    parts = [] 
    if image_file: 
        try: 
            image_bytes = image_file.read() 
            mime_type = image_file.content_type 
            image_base64 = base64.b64encode(image_bytes).decode("utf-8") 
            # Thêm image part 
            parts.append(types.Part( 
                inline_data=types.Blob( 
                    mime_type=mime_type, 
                    data=image_base64 ) 
            )) 
        except Exception as e: 
            logger.error(f"Lỗi khi xử lý ảnh: {e}", exc_info=True) 
            return Response({"error": f"Lỗi khi xử lý ảnh: {str(e)}"}, status=400) 
        
    parts.append(types.Part(text=text_query)) 
    # Khoi tao session 
    # adk_session_id = str(session.id) 
    bot_content = "" 
    try: 
        if not session.adk_session_id:
            adk_session = asyncio.run(create_session("ICD-10", str(user.id)))
            session.adk_session_id = adk_session.id
            session.save()
        # adk_session_id = "session_1" 
        # logger.info(f"Running agent with session_id: {adk_session_id}") 
        content = types.Content(role='user', parts=parts) 
        async def run_agent(): 
            async_events = AGENT_RUNNER.run_async( 
                user_id=str(user.id),
                session_id=session.adk_session_id,
                new_message=content 
            ) 
            results = [] 
            async for event in async_events:
                results.append(event)
            return results
        
        events = asyncio.run(run_agent())
        for event in events: 
            logger.info(f"\nEvent: {event}\n") 
            if event.is_final_response() and event.content: 
                for part in event.content.parts: 
                    if getattr(part, "text", None):
                        bot_content += part.text 
                break 
            
        bot_content = bot_content.strip()
    except Exception as e:
        logger.error(f"Lỗi trong chat_with_ai: {e}", exc_info=True)
        return Response({"error": "Đã xảy ra lỗi khi xử lý yêu cầu."}, status=500) 
    
    if not bot_content: 
        return Response({"error": "Không đủ thông tin chính xác, vui lòng cung cấp mô tả chi tiết hơn hoặc ảnh rõ hơn."}, status=400) 
    
    if image_file: 
        # Lưu ảnh lên S3 
        file_name, presigned_url = Utils.save_file_to_s3(image_file, "chat-bot") 
        user_image = presigned_url 
        
    # Lưu tin nhắn người dùng 
    ChatMessage.objects.create(
        session=session, 
        role="user", 
        content=text_query, 
        image=user_image 
    ) 
    # Lưu phản hồi của bot 
    ChatMessage.objects.create(
        session=session, 
        role="bot", 
        content=bot_content 
    ) 
    
    # Xoá cache để đảm bảo lần GET tiếp theo lấy data mới 
    RedisWrapper.remove(f"{Constants.CACHE_USER_SESSION}_{user.id}") 
    RedisWrapper.remove(f"{Constants.CACHE_MESSAGE_SESSION}_{session.id}") 
    # Gửi text dài về WS bằng Redis (background) 
    async_to_sync(stream_to_ws)(session.id, bot_content) 
    return Response({
        "session_id": session.id,
        "intent": "AI",
        "user_message": { 
            "content": text_query, 
            "image": user_image, 
        }, 
        "bot_message": { 
            "content": bot_content, 
            "source_type": "AGENT", 
        }, 
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_chat_sessions(request):
    cache_sessions = RedisWrapper.get(f"{Constants.CACHE_USER_SESSION}_{request.user.id}")
    if cache_sessions:
        return AppResponse.success(SuccessCodes.GET_USER_CHAT_SESSIONS, data=cache_sessions)
    user = request.user
    sessions = ChatSession.objects.filter(user=user).order_by("-created_at")
    serializer = ChatSessionSerializer(sessions, many=True)
    
    for chat in serializer.data:
        if chat['user']:
            chat['user'] = {
                'id': chat['user'],
                'username': User.objects.get(id=chat['user']).username,
                'avatar': User.objects.get(id=chat['user']).avatar,
                'email': User.objects.get(id=chat['user']).email,
                'first_name': User.objects.get(id=chat['user']).first_name,
                'last_name': User.objects.get(id=chat['user']).last_name
            }
            
    RedisWrapper.save(f"{Constants.CACHE_USER_SESSION}_{user.id}", serializer.data, expire_time=60*15)
    return AppResponse.success(SuccessCodes.GET_USER_CHAT_SESSIONS, data=serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_message_chat_session(request, session_id):
    cache_messages = RedisWrapper.get(f"{Constants.CACHE_MESSAGE_SESSION}_{session_id}")
    if cache_messages:
        return AppResponse.success(SuccessCodes.GET_MESSAGE_CHAT_SESSION, data=cache_messages)
    user = request.user
    session = ChatSession.objects.filter(id=session_id, user=user).first()
    if not session:
        return AppResponse.error(ErrorCodes.CHAT_SESSION_NOT_FOUND)
    messages = ChatMessage.objects.filter(session=session).order_by("created_at")
    serializer = ChatMessageSerializer(messages, many=True)
    
    RedisWrapper.save(f"{Constants.CACHE_MESSAGE_SESSION}_{session_id}", serializer.data, expire_time=60*15)
    return AppResponse.success(SuccessCodes.GET_MESSAGE_CHAT_SESSION, data=serializer.data)