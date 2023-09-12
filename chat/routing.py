from django.conf import settings
from django.urls import re_path
from channels.db import database_sync_to_async
from chat.consumers import  ChatConsumer
import logging
from urllib.parse import parse_qs
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
User = get_user_model()

logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class CustomAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope['query_string'].decode())
        scope['user'] = await get_user(query_string.get('user_id')[0])
        return await self.app(scope, receive, send)

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_id>.*)/$', ChatConsumer.as_asgi()),
]