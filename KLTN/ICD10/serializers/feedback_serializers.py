from ICD10.models.feedback import Feedback_Chapter, Feedback_Block, Feedback_Disease, Feedback_Chatbot
from rest_framework import serializers

class FeedbackChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback_Chapter
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
        
class FeedbackBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback_Block
        fields = ['id', 'user', 'block', 'chapter', 'code', 'title_vi', 'status', 'type_feedback', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']
        
    # def get_chapter(self, obj):
    #     if obj.block and obj.block.chapter:
    #         return obj.block.chapter.code
    #     return None

class FeedbackDiseaseSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Feedback_Disease
        fields = ['id', 'user', 'disease', 'disease_parent', 'block', 'code', 'title_vi', 'status', 'type_feedback', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']
        
    # def get_block(self, obj):
    #     if obj.disease and obj.disease.block:
    #         return obj.disease.block.code
    #     return None
    
    # def get_chapter(self, obj):
    #     if obj.disease and obj.disease.block and obj.disease.block.chapter:
    #         return obj.disease.block.chapter.code
    #     return None

class FeedbackChatbotSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    session = serializers.SerializerMethodField()

    class Meta:
        model = Feedback_Chatbot
        fields = ['id', 'chat_message', 'session', 'rating', 'admin_reply', 'replied_at', 'comments', 'status', 'created_at', 'user']
        read_only_fields = ['id', 'created_at', 'user', 'replied_at']

    def get_user(self, obj):
        return obj.chat_message.session.user.id
    
    def get_session(self, obj):
        return obj.chat_message.session.id
    
    def create(self, validated_data):
        # Loại bỏ user trong validated_data nếu request gửi lên
        validated_data.pop("user", None)
        return Feedback_Chatbot.objects.create(**validated_data)
