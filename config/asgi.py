"""ASGI config for the floos33 backend project with Channels support."""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

import core.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

django_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(
                core.routing.websocket_urlpatterns,
            )
        ),
    }
)
