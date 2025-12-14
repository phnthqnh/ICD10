from rest_framework import serializers
from ICD10.models.chatbot import ChatMessage, ChatSession

class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ['id', 'user', 'title', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']
        
class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'session', 'role', 'content', 'image', 'created_at', 'timestamp']
        read_only_fields = ['id', 'created_at', 'timestamp']