from django.urls import re_path
from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from chat.consumers import ChatConsumer

application = ProtocolTypeRouter({

    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    url(r"^chat/(?P<username>[\w.@+-]+)",ChatConsumer)
                ]
            )
        )
    )
})