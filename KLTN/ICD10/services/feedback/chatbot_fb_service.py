from django.db import transaction
from ICD10.services.feedback.base_feedback_service import BaseFeedbackService
from ICD10.services.notification.notif_service import notify_user_feedback
from django.utils import timezone

class ChatbotFeedbackService(BaseFeedbackService):

    @classmethod
    def handle_admin_reply(cls, feedback, admin_reply):
        if not cls.validate_admin_reply(feedback, admin_reply):
            return False

        feedback.admin_reply = admin_reply
        feedback.replied_at = timezone.now()
        feedback.save(update_fields=["admin_reply", "replied_at"])
        user = feedback.chat_message.session.user
        notify_user_feedback(
            user=user,
            title="Phản hồi Chatbot đã được trả lời",
            message="Phản hồi của bạn về Chatbot đã được quản trị viên trả lời.",
            notif_type="admin_feedback_chatbot",
            url=f"http://localhost:4200/feedback#c#{feedback.id}",
            event="feedback_update",
            feedback_id=feedback.id,
        )
        return True
