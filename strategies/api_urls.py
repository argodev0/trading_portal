"""
URL configuration for strategies API endpoints.
"""

from django.urls import path
from .api_views import (
    GenerateStrategyAPIView,
    StrategyListAPIView,
    StrategyDetailAPIView,
    ValidateStrategyAPIView,
    StrategyGenerationLogsAPIView
)

app_name = 'strategies'

urlpatterns = [
    # Strategy generation
    path('generate/', GenerateStrategyAPIView.as_view(), name='generate-strategy'),
    
    # Strategy CRUD operations
    path('', StrategyListAPIView.as_view(), name='strategy-list'),
    path('<uuid:strategy_id>/', StrategyDetailAPIView.as_view(), name='strategy-detail'),
    
    # Strategy validation
    path('validate/', ValidateStrategyAPIView.as_view(), name='validate-strategy'),
    
    # Generation logs
    path('generation-logs/', StrategyGenerationLogsAPIView.as_view(), name='generation-logs'),
]
