"""
ASGI config for KLTN project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KLTN.settings')
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack
from ICD10.routing import websocket_urlpatterns
# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             websocket_urlpatterns
#         )
#     ),
# })
from ICD10.middleware.jwt_middleware import HybridAuthMiddleware

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": 
        AuthMiddlewareStack(
            HybridAuthMiddleware(
                URLRouter(websocket_urlpatterns)
            )
        )
    ,
})
