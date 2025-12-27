from django.db.models import Count, Max, Sum
import pandas as pd
# views.py
from itertools import chain
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg
import json
from ICD10.models.user import User
from ICD10.models.login_event import LoginEvent
from ICD10.models.api_request_log import ApiRequestLog
from ICD10.models.token_usage import TokenUsage
from ICD10.models.icd10 import ICDDisease, ICDChapter, ICDBlock
from ICD10.models.chatbot import ChatMessage, ChatSession
from ICD10.models.feedback import Feedback_Chapter, Feedback_Block, Feedback_Disease, Feedback_Chatbot
from django.db import models


def dashboard_callback(request, context):
    tab = request.GET.get("tab", "business")

    context.update({
        "active_tab": tab,
    })

    # BUSINESS DASHBOARD
    if tab == "business":
        data = business()
        context.update(data)

    # TECHNICAL DASHBOARD
    if tab == "technical":
        data = technical()
        context.update(data)

    return context


def business():
    today = timezone.now().date()
    
    # Overview
    # 1. tổng số người dùng
    total_users = User.objects.filter(status=1).count()
        
    # 2. tổng session trong ngày
    chat_sessions_today = ChatSession.objects.filter(created_at__date=today).count()
        
    # 3. trung bình rating fb chatbot
    avg_chatbot_rating = Feedback_Chatbot.objects.filter(
        rating__isnull=False
    ).aggregate(avg=Avg("rating"))["avg"]
        
    avg_chatbot_rating = round(avg_chatbot_rating, 2) if avg_chatbot_rating else 0
        
    # 4. số fb icd pending
    pending_feedback = (
        Feedback_Chapter.objects.filter(status=3).count()
        + Feedback_Block.objects.filter(status=3).count()
        + Feedback_Disease.objects.filter(status=3).count()
    )
    
    # Charts
    # 1. số lượng sử dùng chatbot theo ngày (7 ngày)
    last_7_days = today - timedelta(days=7)
    usage_data = []
    
    for i in range(7):
        date = last_7_days + timedelta(days=i)
        sessions = ChatSession.objects.filter(created_at__date=date).count()
        messages = ChatMessage.objects.filter(created_at__date=date).count()
        usage_data.append({
            "date": date.strftime("%d-%m-%Y"), 
            "sessions": sessions,
            "messages": messages
        })
    
    # 2. feedback trend
    feedback_trend = []
    
    for i in range(7):
        date = last_7_days + timedelta(days=i)
        count = (
            Feedback_Chapter.objects.filter(created_at__date=date).count() +
            Feedback_Block.objects.filter(created_at__date=date).count() +
            Feedback_Disease.objects.filter(created_at__date=date).count() +
            Feedback_Chatbot.objects.filter(created_at__date=date).count()
        )
        feedback_trend.append({
            'date': date.strftime("%d-%m-%Y"),
            'count': count
        })
        
    # 3. icd feedback distribution
    chapter_feedback = Feedback_Chapter.objects.count()
    block_feedback = Feedback_Block.objects.count()
    disease_feedback = Feedback_Disease.objects.count()
    
    icd_distribution = [
        {
            "name": "Chapter",
            "value": chapter_feedback
        },
        {
            "name": "Block",
            "value": block_feedback
        },
        {
            "name": "Disease",
            "value": disease_feedback
        }
    ]
    
    # 4. login events (last 7 days) 
    login_events = []
    for i in range(7):
        date = last_7_days + timedelta(days=i)
        success_count = LoginEvent.objects.filter(
            created_at__date=date,
            status="SUCCESS"
        ).count()
        failure_count = LoginEvent.objects.filter(
            created_at__date=date,
            status="FAILURE"
        ).count()
        login_events.append({
            'date': date.strftime("%d-%m-%Y"),
            'success_count': success_count,
            'failure_count': failure_count
        })
    
    # tables
    # 1. latest_feedbacks
    latest_feedbacks = sorted(
        chain(
            Feedback_Chapter.objects.select_related("user").all().values(
                "code",
                "title_vi",
                "status",
                "created_at",
                username=models.F("user__username"),
            ).annotate(type=models.Value("Chapter", output_field=models.CharField())),
            Feedback_Block.objects.select_related("user").all().values(
                "code",
                "title_vi",
                "status",
                "created_at",
                username=models.F("user__username"),
            ).annotate(type=models.Value("Block", output_field=models.CharField())),
            Feedback_Disease.objects.select_related("user").all().values(
                "code",
                "title_vi",
                "status",
                "created_at",
                username=models.F("user__username"),
            ).annotate(type=models.Value("Disease", output_field=models.CharField())),
        ),
        key=lambda x: x["created_at"],
        reverse=True
    )[:10]
    
    # 2. top_icd_feedbacks
    # Top Chapter
    top_chapters = (
        Feedback_Chapter.objects
        .values(
            code_name=models.F("chapter__code"),
            title=models.F("chapter__title_vi"),
        )
        .annotate(
            feedback_count=Count("id"),
            type=models.Value("Chapter", output_field=models.CharField())
        )
        .order_by("-feedback_count")[:10]
    )

    # Top Block
    top_blocks = (
        Feedback_Block.objects
        .values(
            code_name=models.F("block__code"),
            title=models.F("block__title_vi"),
        )
        .annotate(
            feedback_count=Count("id"),
            type=models.Value("Block", output_field=models.CharField())
        )
        .order_by("-feedback_count")[:10]
    )

    # Top Disease
    top_diseases = (
        Feedback_Disease.objects
        .values(
            code_name=models.F("disease__code"),
            title=models.F("disease__title_vi"),
        )
        .annotate(
            feedback_count=Count("id"),
            type=models.Value("Disease", output_field=models.CharField())
        )
        .order_by("-feedback_count")[:10]
    )

    top_icd_feedbacks = list(chain(
        top_chapters,
        top_blocks,
        top_diseases,
    ))[:10]

    
    # 3. worst_rated_chatbots
    worst_chatbot_feedback = (
        Feedback_Chatbot.objects
        .select_related("chat_message__session__user")
        .filter(rating__isnull=False)
        .order_by("rating", "-created_at")
        .values(
            "chat_message__session__user__username",
            "rating",
            "comments",
            "created_at",
            username=models.F("chat_message__session__user__username"),
            message_id=models.F("chat_message__id")
        )[:10]
    )
    
    data = {
        "total_users": total_users,
        "chat_sessions_today": chat_sessions_today,
        "avg_chatbot_rating": avg_chatbot_rating,
        "pending_feedback": pending_feedback,
        "usage_data": json.dumps(usage_data),
        "feedback_trend": json.dumps(feedback_trend),
        "icd_distribution": json.dumps(icd_distribution),
        "login_events": json.dumps(login_events),
        "latest_feedbacks": latest_feedbacks,
        "top_icd_feedbacks": top_icd_feedbacks,
        "worst_chatbot_feedback": worst_chatbot_feedback
    }
    
    return data

def technical():
    today = timezone.now().date()
    
    total_requests = ApiRequestLog.objects.filter(created_at__date=today).count()
    
    error_requests = ApiRequestLog.objects.filter(
        created_at__date=today,
        status_code__gte=400
    ).count()
    
    server_errors_5xx = ApiRequestLog.objects.filter(
        created_at__date=today,
        status_code__gte=500,
        status_code__lt=600
    ).count()
    
    avg_response_time = ApiRequestLog.objects.filter(
        created_at__date=today
    ).aggregate(avg=Avg("response_time_ms"))["avg"]
    
    avg_response_time = round(avg_response_time, 2) if avg_response_time else 0
    
    total_token_usage = TokenUsage.objects.filter(
        created_at__date=today
    ).aggregate(total=Sum("total_tokens"))["total"] or 0
    
    # charts
    # 1. request volume (7 days)
    start_date = today - timedelta(days=7)
    request_volume = []
    
    for i in range(7):
        date = start_date + timedelta(days=i)
        count = ApiRequestLog.objects.filter(created_at__date=date).count()
        request_volume.append({
            "date": date.strftime("%d-%m-%Y"),
            "count": count
        })
        
    # 2. status code distribution
    status_distribution = {
        "2xx": ApiRequestLog.objects.filter(
            status_code__gte=200,
            status_code__lt=300
        ).count(),
        "3xx": ApiRequestLog.objects.filter(
            status_code__gte=300,
            status_code__lt=400
        ).count(),
        "4xx": ApiRequestLog.objects.filter(
            status_code__gte=400,
            status_code__lt=500
        ).count(),
        "5xx": ApiRequestLog.objects.filter(
            status_code__gte=500,
            status_code__lt=600
        ).count(),
    }
    
    status_distribution_chart = [
        {"name": key, "value": value} 
        for key, value in status_distribution.items()
    ]
    
    # 3. error trend (7 days)
    error_trend = []
    for i in range(7):
        date = start_date + timedelta(days=i)
        count = ApiRequestLog.objects.filter(
            created_at__date=date,
            status_code__gte=400
        ).count()
        error_trend.append({
            "date": date.strftime("%d-%m-%Y"),
            "count": count
        })
        
    # 4. token_usage data
    token_usage_data = []
    for i in range(7):
        date = start_date + timedelta(days=i)
        input_tokens = TokenUsage.objects.filter(
            date=date,
        ).aggregate(total=Sum("input_tokens"))["total"] or 0
        output_tokens = TokenUsage.objects.filter(
            date=date,
        ).aggregate(total=Sum("output_tokens"))["total"] or 0
        token_usage_data.append({
            "date": date.strftime("%d-%m-%Y"),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        })
        
    # Tables
    # 1. top failing apis
    top_failing_apis = (
        ApiRequestLog.objects
        .filter(status_code__gte=400)
        .values('path', 'method')
        .annotate(
            error_count=Count("id"),
            last_error=Max("status_code")
        )
        .order_by("-error_count")[:10]
    )
    
    # 2. slowest apis
    slowest_apis = (
        ApiRequestLog.objects
        .values('path', 'method')
        .annotate(
            avg_time=Avg("response_time_ms"),
            max_time=Max("response_time_ms"),
        )
        .order_by("-avg_time")[:10]
    )
    
    # 3. recent errors
    recent_errors = (
        ApiRequestLog.objects
        .filter(status_code__gte=400)
        .select_related('user')
        .order_by("-created_at")[:10]
    )

    data = {
        "total_requests_today": total_requests,
        "error_rate": round(
            (error_requests / total_requests * 100)
            if total_requests else 0,
            2
        ),
        "server_errors_5xx": server_errors_5xx,
        "avg_response_time": avg_response_time,
        "total_token_usage": total_token_usage,
        "request_volume": json.dumps(request_volume),
        "status_distribution": json.dumps(status_distribution_chart),
        "error_trend": json.dumps(error_trend),
        "token_usage_data": json.dumps(token_usage_data),
        "top_failing_apis": top_failing_apis,
        "slowest_apis": slowest_apis,
        "recent_errors": recent_errors
    }
    
    return data