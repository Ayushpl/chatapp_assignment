import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from chat import routing
from channels.auth import AuthMiddlewareStack
from chat.routing import CustomAuthMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatapp.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "https": get_asgi_application(),
        'websocket': CustomAuthMiddleware(URLRouter(
      routing.websocket_urlpatterns
    ),)
    }
)