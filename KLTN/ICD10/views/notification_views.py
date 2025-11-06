from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from constants.constants import Constants
from libs.response_handle import AppResponse
from ICD10.serializers.notification_serializers import NotificationSerializer
from rest_framework import status
from permissions.permisstions import IsAdmin, IsUser
from constants.error_codes import ErrorCodes
from constants.success_codes import SuccessCodes
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
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