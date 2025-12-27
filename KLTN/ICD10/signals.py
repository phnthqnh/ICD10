from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from ICD10.models.feedback import Feedback_Chapter, Feedback_Block, Feedback_Disease, Feedback_Chatbot
from ICD10.models.user import User
from ICD10.models.notification import Notification
from django.db import transaction

def send_ws(group_name, type, event, message, url):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": type,
            "event": event,
            "message": message,
            "url": url,
        },
    )

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
        transaction.on_commit(
            lambda: send_ws(
                group_name="admin_notifications",
                type="send_notification",
                event="new_feedback",
                message=f"{instance.user.username} đã gửi phản hồi cho chương {target_name}",
                url=f"http://127.0.0.1:8000/admin/ICD10/feedback_chapter/{instance.id}/change/"
            )
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
        transaction.on_commit(
            lambda: send_ws(
                group_name="admin_notifications",
                type="send_notification",
                event="new_feedback",
                message=f"{instance.user.username} đã gửi phản hồi cho block {target_name}",
                url=f"http://127.0.0.1:8000/admin/ICD10/feedback_block/{instance.id}/change/"
            )
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
        transaction.on_commit(
            lambda: send_ws(
                group_name="admin_notifications",
                type="send_notification",
                event="new_feedback",
                message=f"{instance.user.username} đã gửi phản hồi cho bệnh {target_name}",
                url=f"http://127.0.0.1:8000/admin/ICD10/feedback_disease/{instance.id}/change/"
            )
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
        transaction.on_commit(
            lambda: send_ws(
                group_name="admin_notifications",
                type="send_notification",
                event="new_feedback",
                message=f"{user.username} đã gửi phản hồi cho tin nhắn {instance.chat_message.id}",
                url=f"http://127.0.0.1:8000/admin/ICD10/feedback_chatbot/{instance.id}/change/"
            )
        )
    
@receiver(pre_save, sender=User)
def store_previous_user(sender, instance, **kwargs):
    if not instance.pk:
        instance._old = None
        return

    try:
        instance._old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        instance._old = None

@receiver(post_save, sender=User)
def notify_admin_verify_request(sender, instance, created, **kwargs):
    """
    Gửi thông báo cho admin khi user tải lên file xác minh bác sĩ
    """
    if instance.is_superuser:
        return
    
    old = getattr(instance, "_old", None)

    if not old:
        return
        
    is_first_verify = (
        not old.verification_file and
        instance.verification_file and
        not instance.is_verified_doctor
    )
    
    is_update_verify = (
        old.verification_file and
        not instance.is_verified_doctor and
        (
            old.verification_file != instance.verification_file or
            old.license_number != instance.license_number or
            old.hospital != instance.hospital
        )
    )

    print('previous:', old.verification_file)
    print('instance:', instance.verification_file)
    
    if not (is_first_verify or is_update_verify):
        return
    
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
    transaction.on_commit(
        lambda: send_ws(
            group_name="admin_notifications",
            type="send_notification",
            event="verify_request",
            message=f"🩺 {instance.username} vừa gửi yêu cầu xác minh bác sĩ",
            url=f"http://127.0.0.1:8000/admin/ICD10/user/{instance.id}/change/"
        )
    )
