from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from ICD10.models.feedback import Feedback_Chapter, Feedback_Block, Feedback_Disease, Feedback_Chatbot
from ICD10.models.user import User
from ICD10.models.notification import Notification

@receiver(post_save, sender=Feedback_Chapter)
def notify_admin_new_feedback_chapter(sender, instance, created, **kwargs):
    if not created:
        return
    
    if created:
        try:
            target_name = instance.chapter.code
        except:
            return
        # Gửi notification trong DB
        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                title="Phản hồi về chương ICD-10",
                message=f"{instance.user.username} đã gửi phản hồi cho chương {target_name}",
                url=f"http://127.0.0.1:8000/admin/ICD10/feedback_chapter/{instance.id}/change/",
                notif_type='feedback'
            )
        # Gửi realtime websocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "admin_notifications",
            {
                "type": "send_notification",
                "event": "new_feedback",
                "message": f"{instance.user.username} đã gửi phản hồi cho chương {target_name}",
                "url": f"http://127.0.0.1:8000/admin/ICD10/feedback_chapter/{instance.id}/change/"
            },
        )
        
@receiver(post_save, sender=Feedback_Block)
def notify_admin_new_feedback_block(sender, instance, created, **kwargs):
    if not created:
        return
    
    if created:
        try:
            target_name = instance.block.code
        except:
            return
        # Gửi notification trong DB
        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                title="Phản hồi về nhóm ICD-10",
                message=f"{instance.user.username} đã gửi phản hồi cho block {target_name}",
                url=f"http://127.0.0.1:8000/admin/ICD10/feedback_block/{instance.id}/change/",
                notif_type='feedback'
            )
        # Gửi realtime websocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "admin_notifications",
            {
                "type": "send_notification",
                "event": "new_feedback",
                "message": f"{instance.user.username} đã gửi phản hồi cho block {target_name}",
                "url": f"http://127.0.0.1:8000/admin/ICD10/feedback_block/{instance.id}/change/"
            },
        )
        
@receiver(post_save, sender=Feedback_Disease)
def notify_admin_new_feedback_disease(sender, instance, created, **kwargs):
    if not created:
        return
    if created:
        try:
            target_name = instance.disease.code
        except:
            return
        # Gửi notification trong DB
        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                title="Phản hồi về bệnh ICD-10",
                message=f"{instance.user.username} đã gửi phản hồi cho bệnh {target_name}",
                url=f"http://127.0.0.1:8000/admin/ICD10/feedback_disease/{instance.id}/change/",
                notif_type='feedback'
            )
        # Gửi realtime websocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "admin_notifications",
            {
                "type": "send_notification",
                "event": "new_feedback",
                "message": f"{instance.user.username} đã gửi phản hồi cho bệnh {target_name}",
                "url": f"http://127.0.0.1:8000/admin/ICD10/feedback_disease/{instance.id}/change/"
            },
        )
        
@receiver(post_save, sender=Feedback_Chatbot)
def notify_admin_new_feedback_chatbot(sender, instance, created, **kwargs):
    if not created:
        return
    if created:
        try:
            chat_message = instance.chat_message
        except:
            return
        # Gửi notification trong DB
        user = chat_message.session.user
        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                title="Phản hồi về Chatbot",
                message=f"{user.username} đã gửi phản hồi cho tin nhắn {instance.chat_message.id}",
                url=f"http://127.0.0.1:8000/admin/ICD10/feedback_chatbot/{instance.id}/change/",
                notif_type='feedback'
            )
        # Gửi realtime websocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "admin_notifications",
            {
                "type": "send_notification",
                "event": "new_feedback",
                "message": f"{user.username} đã gửi phản hồi cho tin nhắn {instance.chat_message.id}",
                "url": f"http://127.0.0.1:8000/admin/ICD10/feedback_chatbot/{instance.id}/change/"
            },
        )

@receiver(post_save, sender=User)
def notify_admin_verify_request(sender, instance, created, **kwargs):
    """
    Gửi thông báo cho admin khi user tải lên file xác minh bác sĩ
    """
    # Nếu user KHÔNG phải là admin và có file xác minh
    if not instance.is_superuser and instance.verification_file and not instance.is_verified_doctor:
        # Gửi notification trong DB
        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                title="Yêu cầu xác minh bác sĩ mới",
                message=f"🩺 {instance.username} vừa gửi yêu cầu xác minh bác sĩ",
                url=f"http://127.0.0.1:8000/admin/ICD10/user/{instance.id}/change/",
                notif_type='verify'
            )
        # Gửi realtime websocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "admin_notifications",
            {
                "type": "send_notification",
                "event": "verify_request",
                "message": f"🩺 {instance.username} vừa gửi yêu cầu xác minh bác sĩ",
                "url": f"http://127.0.0.1:8000/admin/ICD10/user/{instance.id}/change/"
            },
        )
