from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db import transaction
from asgiref.sync import sync_to_async
import json
from ICD10.models.chatbot import ChatSession, ChatMessage
from ICD10.models.user import User
from ICD10.models.notification import Notification
from ICD10.services.chat_services import GeminiChatService
import logging
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from django.utils.timezone import localtime

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope["query_string"].decode()
        token = parse_qs(query_string).get("token", [None])[0]
        self.scope["user"] = await self.get_user_from_token(token)
        
        if self.scope["user"].is_anonymous:
            await self.close()
            print("❌ Anonymous user - closing WebSocket")
            return
        await self.accept()
        # await self.send_json({"type": "system", "message": "✅ Connected to ICD10 AI Chat"})

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
            
    @database_sync_to_async
    def get_user_from_token(self, token):
        if not token:
            return AnonymousUser()
        try:
            validated_token = AccessToken(token)
            user_id = validated_token["user_id"]
            return User.objects.get(id=user_id)
        except Exception:
            return AnonymousUser()
    
    @database_sync_to_async
    def get_user(self):
        return User.objects.get(username=self.scope['user'].username)
    
    @database_sync_to_async
    def _save_message(self, session, role, content, image=None):
        return ChatMessage.objects.create(
            session=session,
            role=role,
            content=content,
            image=image
        )

    @database_sync_to_async
    def _count_messages(self, session):
        return ChatMessage.objects.filter(session=session).count()

    async def receive(self, text_data):
        data = json.loads(text_data)
        text_query = data.get("text", "").strip()
        session_id = data.get("session_id", None)
        image_url = data.get("image", None)

        user = self.scope["user"]

        if not text_query and not image_url:
            await self.send_json({"error": "Vui lòng nhập tin nhắn hoặc tải ảnh."})
            return

        try:
            chat_service = GeminiChatService()

            # --- Gọi AI ---
            def process_transaction():
                with transaction.atomic():
                    # Lấy hoặc tạo session
                    if session_id:
                        session = ChatSession.objects.get(id=session_id, user=user)
                    else:
                        session = ChatSession(user=user)
                        session.save()
                    if image_url:
                        response_data = chat_service._process_query(text_query, user=user, image_file=image_url)
                    else:
                        response_data = chat_service._process_query(text_query, user=user)
                        
                    return session, response_data

            session, response_data = await sync_to_async(process_transaction)()
            
            # --- Lưu tin nhắn ---
            # Lưu message user
            user_msg = await self._save_message(session, "user", text_query, image_url)

            # Lưu phản hồi bot
            bot_msg = await self._save_message(session, "bot", response_data["content"])

            # --- Kiểm tra tóm tắt ---  
            total = await self._count_messages(session)
            if total >= (session.summary_count + 1) * 20:
                await chat_service.summarize_conversation(session.id)
                session.summary_count += 1
                await session.save()

            # --- Gửi lại phản hồi ---
            await self.send_json({
                "session_id": session.id,
                "user_message": {
                    "id": user_msg.id,
                    "content": text_query,
                    "created_at": str(user_msg.created_at),
                },
                "bot_message": {
                    "id": bot_msg.id,
                    "content": response_data["content"],
                    "created_at": str(bot_msg.created_at),
                },
            })

        except Exception as e:
            logger.error(f"Lỗi trong ChatConsumer: {e}", exc_info=True)
            await self.send_json({"error": "Đã xảy ra lỗi khi xử lý tin nhắn."})


    async def send_json(self, content):
        await self.send(text_data=json.dumps(content))
    
    async def chat_message(self, event):
        await self.send_json({
            'message': event['message'],
            'role': event["role"]
        })


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # query_string = self.scope["query_string"].decode()
        # token = parse_qs(query_string).get("token", [None])[0]
        # self.scope["user"] = await self.get_user_from_token(token)
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return

        # Lưu room_group_name cho user
        self.room_group_name = f"user_{self.scope['user'].id}"
        
        # Join vào group của user
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Nếu là admin, thêm vào group admin
        if self.scope["user"].is_superuser:
            await self.channel_layer.group_add(
                "admin_notifications", 
                self.channel_name
            )
            
        await self.accept()
        
        # Gửi data ban đầu
        await self.send_initial_data()
        
    async def send_initial_data(self):
        """Gửi notifications data khi user kết nối"""
        notifications = await self.get_notifications()
        await self.send_json({
            'type': 'notifications_data',
            'notifications': notifications,
            'unread_count': await self.get_unread_count()
        })

    async def disconnect(self, code):
        user = self.scope["user"]
        await self.channel_layer.group_discard(f"user_{user.id}", self.channel_name)
        if user.is_superuser:
            await self.channel_layer.group_discard("admin_notifications", self.channel_name)
        # await self.channel_layer.group_discard(
        #     self.room_group_name,
        #     self.channel_name
        # )
        
    @database_sync_to_async
    def get_notifications(self):
        return [{
            'id': notif.id,
            'title': notif.title,
            'message': notif.message,
            # 'created_at': notif.created_at.strftime("%d/%m/%Y %H:%M"),
            'created_at': localtime(notif.created_at).strftime("%d/%m/%Y %H:%M"),
            'is_read': notif.is_read
        } for notif in Notification.objects.filter(
            recipient=self.scope["user"]
        ).order_by('-created_at')[:5]]

    @database_sync_to_async
    def get_unread_count(self):
        return Notification.objects.filter(
            recipient=self.scope["user"],
            is_read=False
        ).count()


    @database_sync_to_async
    def get_user_from_token(self, token):
        if not token:
            return AnonymousUser()
        try:
            validated_token = AccessToken(token)
            user_id = validated_token["user_id"]
            return User.objects.get(id=user_id)
        except Exception:
            return AnonymousUser()
    
    async def receive(self, text_data):
        # Có thể dùng để test client gửi message
        data = json.loads(text_data)
        await self.send(text_data=json.dumps({
            "message": f"Received: {data}"
        }))

    async def send_notification(self, event):
        """
        Nhận thông báo từ group và gửi về client
        """
        notifications = await self.get_notifications()
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            "type": "new_notification",
            "event": event["event"],
            "message": event["message"],
            "notifications": notifications,
            "unread_count": unread_count
        }))
        
    async def send_json(self, content):
        """Gửi JSON response với error handling"""
        try:
            await self.send(text_data=json.dumps(content))
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            