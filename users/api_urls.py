from django.urls import path, include
from .api_views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    UserRegistrationView,
    UserProfileView,
    LogoutView,
    protected_view,
    api_info,
)

app_name = 'users_api'

urlpatterns = [
    # JWT Authentication endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    # User management endpoints
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Test endpoints
    path('protected/', protected_view, name='protected'),
    path('info/', api_info, name='api_info'),
]
