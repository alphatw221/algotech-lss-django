"""
ASGI config for lss project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""
import config
import os

# from channels.auth import AuthMiddlewareStack
from django_channels_jwt_auth_middleware.auth import JWTAuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import lss.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', config.DJANGO_SETTINGS)

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Just HTTP for now. (We can add other protocols later.)
    "websocket": JWTAuthMiddlewareStack(
        URLRouter(
            lss.routing.websocket_urlpatterns
        )
    ),

})