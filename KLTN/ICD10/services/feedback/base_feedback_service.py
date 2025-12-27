from django.db import transaction


class BaseFeedbackService:
    """
    Base service cho feedback
    """

    STATUS_PENDING = 3
    STATUS_ACCEPTED = 1
    STATUS_REJECTED = 2

    @classmethod
    def validate_status(cls, feedback):
        if feedback.status == cls.STATUS_PENDING:
            return False
        return True

    @classmethod
    def validate_admin_reply(cls, feedback, admin_reply) -> bool:
        """
        Admin chỉ được reply 1 lần duy nhất
        """

        # Không có nội dung reply
        if not admin_reply:
            return False

        # Đã reply trước đó → không cho sửa
        if feedback.replied_at is not None:
            return False

        return True
