from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/balances/$', consumers.BalanceConsumer.as_asgi()),
    re_path(r'ws/prices/$', consumers.PriceConsumer.as_asgi()),
]
