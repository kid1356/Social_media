from django.urls import re_path
from .consumers import NotificationConsumer


websocket_patterns = [
    re_path(r"ws/notify/", NotificationConsumer.as_asgi()),
]
