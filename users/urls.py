from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('stats/', views.user_stats, name='user_stats'),
]
