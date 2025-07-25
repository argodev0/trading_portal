"""
URL configuration for trading_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .health_views import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('django/', include('users.urls')),  # Changed from '' to 'django/'
    path('api/health/', health_check, name='health-check'),
    path('api/auth/', include('users.api_urls')),
    path('api/accounts/', include('exchanges.api_urls')),
    path('api/exchanges/', include('exchanges.api_urls')),  # Add explicit exchanges route
    path('api/strategies/', include('strategies.api_urls')),
    path('api/bots/', include('bots.api_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
