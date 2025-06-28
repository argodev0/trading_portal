from django.urls import path
from .api_views import UserAPIKeysView, UserAPIKeyDetailView

urlpatterns = [
    # API Keys management
    path('keys/', UserAPIKeysView.as_view(), name='user-api-keys'),
    path('keys/<uuid:pk>/', UserAPIKeyDetailView.as_view(), name='user-api-key-detail'),
]
