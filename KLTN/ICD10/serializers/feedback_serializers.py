from ICD10.models.feedback import Feedback_ICD10, Feedback_Chatbot
from rest_framework import serializers

class FeedbackICD10Serializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback_ICD10
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class FeedbackChatbotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback_Chatbot
        fields = '__all__'
        read_only_fields = ['id', 'created_at']