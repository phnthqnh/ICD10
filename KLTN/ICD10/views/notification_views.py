from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from libs.response_handle import AppResponse
from ICD10.serializers.notification_serializers import NotificationSerializer
from rest_framework import status
from permissions.permisstions import IsAdmin, IsUser
from constants.error_codes import ErrorCodes
from constants.success_codes import SuccessCodes
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from ICD10.models.notification import Notification
from django.utils import timezone

@login_required
def unread_notifications(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({"unread_count": count})


def notification_badge_callback(request):
    c= Notification.objects.filter(
        recipient=request.user,
        is_read=False,
        created_at__gte= timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)).count()
    if c==0:
        return ''
    print("Notification badge callback count:", c)
    return f"+{c}"

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsUser])
def user_notifications(request):
    user = request.user
    notifications = Notification.objects.filter(recipient=user).order_by("-created_at")
    serializer = NotificationSerializer(notifications, many=True)
    un_read_count = notifications.filter(is_read=False).count()
    return AppResponse.success(
        SuccessCodes.GET_USER_NOTIFICATIONS,
        data={
            "notifications": serializer.data,
            "unread_count": un_read_count
        }
    )
    
@login_required
def unread_notis(request):
    # Lấy 5 notifications gần nhất
    recent_notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:5]

    # Serialize notifications
    notifications_data = [{
        'title': notif.title,
        'message': notif.message,
        'created_at': notif.created_at.strftime("%d/%m/%Y %H:%M"),
        'is_read': notif.is_read
    } for notif in recent_notifications]

    # Đếm tổng số notification chưa đọc
    unread_count = Notification.objects.filter(
        recipient=request.user, 
        is_read=False
    ).count()

    return JsonResponse({
        "unread_count": unread_count,
        "notifications": notifications_data
    })
    
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsUser])
def mark_notifications_as_read(request, pk):
    user = request.user
    is_read = request.data.get("is_read")

    if is_read is None:
        return AppResponse.error(
            ErrorCodes.INVALID_REQUEST,
            errors="Missing `is_read` field"
        )
        
    notification = Notification.objects.filter(id=pk, recipient=user).first()
    if not notification:
        return AppResponse.error(
            ErrorCodes.NOT_FOUND,
            errors="Notification not found"
        )
        
    notification.is_read = bool(is_read)
    notification.save()
    
    return AppResponse.success(
        SuccessCodes.MARK_NOTIFICATIONS_AS_READ,
        data={"is_read": notification.is_read}
    )
    
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsUser])
def mark_all_notifications_as_read(request):
    user = request.user
    Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)
    return AppResponse.success(
        SuccessCodes.MARK_ALL_NOTIFICATIONS_AS_READ
    )
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsUser])
def delete_notification(request, pk):
    user = request.user
    notification = Notification.objects.filter(id=pk, recipient=user).first()
    if not notification:
        return AppResponse.error(
            ErrorCodes.NOT_FOUND,
            errors="Notification not found"
        )
    notification.delete()
    return AppResponse.success(
        SuccessCodes.DELETE_NOTIFICATION
    )
    
    
@login_required
@require_POST
def admin_notification_read(request, notif_id):
    try:
        notif = Notification.objects.get(id=notif_id, recipient=request.user)
        if not notif.is_read:
            notif.is_read = True
            notif.save(update_fields=["is_read"])
        return JsonResponse({"success": True})
    except Notification.DoesNotExist:
        return JsonResponse({"success": False}, status=404)