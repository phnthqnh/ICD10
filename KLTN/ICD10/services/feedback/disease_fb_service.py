from django.db import transaction
from ICD10.services.feedback.base_feedback_service import BaseFeedbackService
from ICD10.services.notification.notif_service import notify_user_feedback

class DiseaseFeedbackService(BaseFeedbackService):

    @classmethod
    @transaction.atomic
    def handle(cls, feedback):
        if not cls.validate_status(feedback):
            return

        disease = feedback.disease
        user = feedback.user

        if feedback.status == cls.STATUS_ACCEPTED:
            cls._apply_changes(feedback, disease)
            cls._notify_accepted(user, disease, feedback)

        elif feedback.status == cls.STATUS_REJECTED:
            cls._notify_rejected(user, disease, feedback)

    @staticmethod
    def _apply_changes(feedback, disease):
        if feedback.code:
            disease.code = feedback.code
        if feedback.title_vi:
            disease.title_vi = feedback.title_vi
        if feedback.block:
            disease.block = feedback.block
        if feedback.disease_parent:
            disease.parent = feedback.disease_parent

        disease.save()

    @staticmethod
    def _notify_accepted(user, disease, feedback):
        if disease.parent:
            level = 3
        else:
            level = 2
        notify_user_feedback(
            user=user,
            title="Phản hồi ICD-10 được chấp nhận",
            message=f"Phản hồi về bệnh {disease.code} đã được chấp nhận",
            notif_type="admin_feedback_icd",
            url=f"http://localhost:4200/icd-10#/{level}#{disease.code}",
            event="feedback_update",
            feedback_id=feedback.id,
        )

    @staticmethod
    def _notify_rejected(user, disease, feedback):
        notify_user_feedback(
            user=user,
            title="Phản hồi ICD-10 bị từ chối",
            message=f"Phản hồi về bệnh {disease.code} đã bị từ chối",
            notif_type="admin_feedback_icd",
            url=f"http://localhost:4200/feedback#2#{feedback.id}",
            event="feedback_update",
            feedback_id=feedback.id,
        )
