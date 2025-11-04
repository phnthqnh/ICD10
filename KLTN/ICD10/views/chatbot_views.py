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

import os
import requests
import json
import logging
import base64
from django.urls import reverse
from django.conf import settings
from ICD10.services.chat_services import GeminiChatService
from django.db import transaction

# Khởi tạo logger
logger = logging.getLogger(__name__)

# chat with ai
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def chat_with_ai(request):
    """
    API chính để người dùng trò chuyện với chatbot y tế ICD10.
    - Nhận `text` (bắt buộc) và `image` (tùy chọn).
    - Có thể truyền `session_id` để tiếp tục hội thoại cũ.
    """
    user = request.user
    text_query = request.data.get("text", "").strip()
    image_file = request.FILES.get("image", None)
    session_id = request.data.get("session_id")

    if not text_query and not image_file:
        return Response({"error": "Vui lòng nhập tin nhắn hoặc tải ảnh."}, status=400)

    try:
        chat_service = GeminiChatService()

        # Nếu có session_id → lấy session cũ, nếu không → tạo mới
        session = (
            ChatSession.objects.filter(id=session_id, user=user).first()
            if session_id
            else ChatSession.objects.create(user=user)
        )


        # --- Xử lý hội thoại ---
        if image_file:
            response_data = chat_service._process_query(text_query, user=user, image_file=image_file)
        else:
            response_data = chat_service._process_query(text_query, user=user)
            
        # Nếu có ảnh, lưu vào S3
        file_name = None
        if image_file:
            file_name, _ = Utils.save_file_to_s3(image_file, "chat-bot")

        # Lưu tin nhắn người dùng
        ChatMessage.objects.create(
            session=session,
            role="user",
            content=text_query,
            image=file_name
        )
        
        # Lưu phản hồi của bot
        bot_message = ChatMessage.objects.create(
            session=session,
            role="bot",
            content=response_data["content"]
        )

        # --- Kiểm tra điều kiện tóm tắt ---
        total_msgs = ChatMessage.objects.filter(session=session).count()
        if total_msgs >= (session.summary_count + 1) * 20:
            chat_service.summarize_conversation(session.id)
            session.summary_count += 1
            session.save()

        # --- Trả kết quả ---
        return Response({
            "session_id": session.id,
            "intent": response_data.get("source_type", "AI"),
            "user_message": {
                "content": text_query,
                "image": file_name,
            },
            "bot_message": {
                "content": response_data["content"],
                "source_type": response_data.get("source_type", "AI"),
            },
        })

    except Exception as e:
        logger.error(f"Lỗi trong chat_with_ai: {e}", exc_info=True)
        return Response({"error": "Đã xảy ra lỗi khi xử lý yêu cầu."}, status=500)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def ai_predict_disease(request):
#     """
#     Nhận hình ảnh và/hoặc văn bản triệu chứng, trả về một danh sách các từ khóa bệnh lý.
#     """
#     if not settings.GEMINI_API_KEY:
#         logger.error("GEMINI_API_KEY is not configured in environment variables.")
#         return Response({"error": "Server is not configured correctly."}, status=503) # Service Unavailable

#     user = request.user
#     session_id = request.data.get("session_id")

#     # 1️⃣ Lấy hoặc tạo session
#     session = ChatSession.objects.filter(id=session_id).first() if session_id else ChatSession.objects.create(user=user)

#     image_file = request.FILES.get("image", None)
#     text_query = request.data.get("text")

#     if not image_file and not text_query:
#         return Response({"error": "No image or text provided."}, status=400)
    
#     file_name = None
#     if image_file:
#         image_bytes = image_file.read()
#         image_base64 = base64.b64encode(image_bytes).decode("utf-8")
#         mime_type = image_file.content_type  # ví dụ: image/jpeg, image/png
#         file_name, presigned_url = Utils.save_file_to_s3(image_file, "chat-bot")
#         if not file_name or not presigned_url:
#             return AppResponse.error(ErrorCodes.INTERNAL_SERVER_ERROR, errors="Failed to upload file")
    
#     # ✅ 3️⃣ Lưu tin nhắn người dùng (có thể gồm cả text và image)
#     ChatMessage.objects.create(
#         session=session,
#         role="user",
#         content=text_query,
#         image=file_name,  # lưu tên file đã upload lên S3
#     )
    
#     # --- 4️⃣ Cache kiểm tra ---
#     cache_key = f"ai_predict_{hash(text_query)}"
#     cached_result = RedisWrapper.get(cache_key)
#     if cached_result:
#         logger.info("Using cached AI result.")
#         return Response(cached_result)
    
#     parts = []
    
#      # 1. Xử lý và thêm phần văn bản vào payload
#     if text_query and not image_file:
#         prompt_text = Constants.PROMPT_AI_TEXT.replace("{text_query}", text_query)
#         parts.append({"text": prompt_text})
#     elif image_file and text_query:
#         prompt_text = Constants.PROMPT_AI_IMAGE.replace("{text_query}", text_query)
#         parts.append({"text": prompt_text})
#         parts.append({
#             "inline_data": {
#                 "mime_type": mime_type,
#                 "data": image_base64
#             }    
#         })
#     else:
#         return Response({"error": "Invalid request."}, status=400)
    
#     payload = {"contents": [{"parts": parts}]}
#     headers = {"Content-Type": "application/json"}
#     try:
#         response = requests.post(
#             f"{Constants.GEMINI_API_URL}?key={settings.GEMINI_API_KEY}", 
#             headers=headers, 
#             json=payload,
#             timeout=Constants.REQUEST_TIMEOUT 
#         )
#         response.raise_for_status()  # Tự động báo lỗi nếu status code là 4xx hoặc 5xx
#         data = response.json()
#         text_output = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
#         keywords = json.loads(text_output)

#     except requests.exceptions.Timeout:
#         logger.error("Request to Gemini API timed out.")
#         return Response({"error": "The request to the AI service timed out."}, status=504) # Gateway Timeout
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Gemini API request failed: {e}")
#         return Response({"error": "Gemini API request failed", "details": str(e)}, status=500)

#     diseases = []
#     try:
#         search_url = request.build_absolute_uri(reverse("ai_search_disease_gemini"))
#         print("search_url:", search_url)
#         search_response = requests.get(search_url, params={"q": json.dumps(keywords)}, timeout=Constants.REQUEST_TIMEOUT)
#         search_response.raise_for_status()
#         diseases = search_response.json().get("results", [])
#     except Exception as e:
#         logger.error(f"Search disease failed after prediction: {e}")
        
#     # ✅ Lưu phản hồi chatbot
#     ChatMessage.objects.create(
#         session=session,
#         role="bot",
#         content=f"Kết quả AI: {json.dumps({'keywords': keywords, 'diseases': diseases}, ensure_ascii=False)}"
#     )
#      # --- 9️⃣ Cache kết quả ---
#     RedisWrapper.save(cache_key, {"keywords": keywords, "diseases": diseases}, expire_time=3600)
    
#     # 5️⃣ Nếu đạt 20 message kể từ lần tóm tắt trước → tạo summary mới
#     total_msgs = ChatMessage.objects.filter(session=session).count()
#     if total_msgs >= (session.summary_count + 1) * 20:
#         Utils._generate_chat_summary(session, gemini_api_key)
#         session.summary_count += 1
#         session.save()
        
#     return Response({
#         "session_id": session.id,
#         "keywords": keywords,
#         "diseases": diseases
#     })
