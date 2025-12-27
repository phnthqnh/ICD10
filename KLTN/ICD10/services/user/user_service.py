from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from ICD10.models import User
from ..notification.notif_service import notify_verify_doctor
from utils.utils import Utils

class UserService:
    """
    Service xử lý toàn bộ business logic cho User
    """

    @classmethod
    def handle_role_by_doctor_status(cls, user: User):
        """
        Nếu user được verify doctor → set role
        """
        if user.is_verified_doctor:
            user.role = 2  # nên dùng constant
            user.save(update_fields=["role"])

    @classmethod
    def send_activation_email_for_new_user(cls, user: User, raw_password: str):
        """
        Gửi email kích hoạt sau khi admin tạo user
        """
        if not raw_password:
            return

        token = Utils.generate_verification_token(user)
        activation_link = f"{settings.ACTIVATION_URL}?token={token}"

        Utils.admin_send_activation_email(
            user=user,
            password=raw_password,
            activation_link=activation_link,
        )

    @classmethod
    def notify_doctor_verified(cls, user: User):
        """
        Notify khi bác sĩ được xác thực
        """
        notify_verify_doctor(
            user=user,
            title="Xác nhận bác sĩ thành công",
            message="Chúc mừng! Tài khoản bác sĩ của bạn đã được xác thực",
            notif_type="admin_doctor",
            url="http://localhost:4200/profile",
            role=user.role,
        )
