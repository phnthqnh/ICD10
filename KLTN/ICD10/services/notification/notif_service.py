from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from ICD10.models.notification import Notification
from django.db import transaction

def send_ws_feedback(group_name, type, event, message, url, feedback_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": type,
            "event": event,
            "message": message,
            "url": url,
            "feedback_id": feedback_id,
        },
    )
    
def send_ws_doctor(group_name, type, event, message, url, role):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": type,
            "event": event,
            "message": message,
            "url": url,
            "role": role,
        },
    )

def notify_user_feedback(
    *,
    user,
    title,
    message,
    notif_type,
    url,
    event,
    feedback_id,
):
    """
    Gửi notification + websocket cho user
    """
    Notification.objects.create(
        recipient=user,
        title=title,
        message=message,
        notif_type=notif_type,
        url=url,
    )
    
    transaction.on_commit(
        lambda: send_ws_feedback(
            group_name=f"user_{user.id}",
            type="send_notification",
            event=event,
            message=message,
            url=url,
            feedback_id=feedback_id,
        )
    )

def notify_verify_doctor(
    *,
    user,
    title,
    message,
    notif_type,
    url,
    role,
):
    """
    Gửi notification + websocket cho user
    """
    Notification.objects.create(
        recipient=user,
        title=title,
        message=message,
        notif_type=notif_type,
        url=url,
    )
    
    transaction.on_commit(
        lambda: send_ws_doctor(
            group_name=f"user_{user.id}",
            type="send_notification",
            event="verification_doctor",
            message=message,
            url=url,
            role=role,
        )
    )

