from django.urls import path
from .api_views import (
    UserAPIKeysView, 
    UserAPIKeyDetailView, 
    UserBalancesView,
    ExchangeConnectionStatusView,
    WebSocketStreamView,
    RealTimeConnectionTestView
)

urlpatterns = [
    path('keys/', UserAPIKeysView.as_view(), name='user-api-keys'),
    path('keys/<int:pk>/', UserAPIKeyDetailView.as_view(), name='user-api-key-detail'),
    path('balances/', UserBalancesView.as_view(), name='user-balances'),
    path('websocket/capabilities/', WebSocketStreamView.as_view(), name='websocket-capabilities'),
    path('websocket/test/', RealTimeConnectionTestView.as_view(), name='websocket-test'),
    path('<str:exchange_name>/status/', ExchangeConnectionStatusView.as_view(), name='exchange-connection-status'),
]
