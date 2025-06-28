"""
URL configuration for bots API endpoints.
"""

from django.urls import path
from .api_views import (
    BotListAPIView,
    BotDetailAPIView,
    BotStartAPIView,
    BotStopAPIView,
    BotRunsAPIView,
    BotStatusAPIView
)

app_name = 'bots'

urlpatterns = [
    # Bot CRUD operations
    path('', BotListAPIView.as_view(), name='bot-list'),
    path('<uuid:bot_id>/', BotDetailAPIView.as_view(), name='bot-detail'),
    
    # Bot control operations
    path('<uuid:bot_id>/start/', BotStartAPIView.as_view(), name='bot-start'),
    path('<uuid:bot_id>/stop/', BotStopAPIView.as_view(), name='bot-stop'),
    path('<uuid:bot_id>/status/', BotStatusAPIView.as_view(), name='bot-status'),
    
    # Bot runs
    path('<uuid:bot_id>/runs/', BotRunsAPIView.as_view(), name='bot-runs'),
]
