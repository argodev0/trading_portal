from django.urls import path
from .api_views import UserAPIKeysView, UserAPIKeyDetailView, UserBalancesView

urlpatterns = [
    # API Keys management
    path('keys/', UserAPIKeysView.as_view(), name='user-api-keys'),
    path('keys/<uuid:pk>/', UserAPIKeyDetailView.as_view(), name='user-api-key-detail'),
    
    # Balances
    path('balances/', UserBalancesView.as_view(), name='user-balances'),
]
