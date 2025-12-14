from django.urls import path, re_path
from ICD10.consumers import AIStreamConsumer, NotificationConsumer

websocket_urlpatterns = [
    re_path(r"^ws/ai-stream/?$", AIStreamConsumer.as_asgi()),
    path("ws/notifications/", NotificationConsumer.as_asgi()),
]
