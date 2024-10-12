import os
from .custom_auth import CustomAuthMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "facebook.settings")
django_asgi_app = get_asgi_application()

from messanger.routing import websocket_patterns as chats_socket_patterns
from posting_blogs.routing import websocket_patterns




# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facebook.settings')


# application  = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http" : django_asgi_app,
        "websocket" : AllowedHostsOriginValidator(
            CustomAuthMiddleware(
                URLRouter(
                    websocket_patterns + chats_socket_patterns
                )
            )
        )
    }
)
