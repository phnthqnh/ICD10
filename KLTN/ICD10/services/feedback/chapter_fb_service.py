from django.db import transaction
from ICD10.services.feedback.base_feedback_service import BaseFeedbackService
from ICD10.services.notification.notif_service import notify_user_feedback


class ChapterFeedbackService(BaseFeedbackService):

    @classmethod
    @transaction.atomic
    def handle(cls, feedback):
        if not cls.validate_status(feedback):
            return

        chapter = feedback.chapter
        user = feedback.user

        if feedback.status == cls.STATUS_ACCEPTED:
            if feedback.code:
                chapter.code = feedback.code
            if feedback.title_vi:
                chapter.title_vi = feedback.title_vi
            chapter.save()

            notify_user_feedback(
                user=user,
                title="Phản hồi ICD-10 được chấp nhận",
                message=f"Phản hồi về chương {chapter.code} đã được chấp nhận",
                notif_type="admin_feedback_icd",
                url=f"http://localhost:4200/icd-10#/0#{chapter.code}",
                event="feedback_update",
                feedback_id=feedback.id,
            )

        elif feedback.status == cls.STATUS_REJECTED:
            notify_user_feedback(
                user=user,
                title="Phản hồi ICD-10 bị từ chối",
                message=f"Phản hồi về chương {chapter.code} đã bị từ chối",
                notif_type="admin_feedback_icd",
                url=f"http://localhost:4200/feedback#0#{feedback.id}",
                event="feedback_update",
                feedback_id=feedback.id,
            )
