from django.shortcuts import render
from django.http import HttpResponse
from .models import User

def index(request):
    return HttpResponse("Welcome to Trading Portal - Users App is working!")

def home(request):
    return render(request, 'users/home.html')

def user_stats(request):
    """Display user statistics showing the custom User model in action"""
    total_users = User.objects.count()
    free_users = User.objects.filter(account_tier='Free').count()
    premium_users = User.objects.filter(account_tier='Premium').count()
    
    context = {
        'total_users': total_users,
        'free_users': free_users,
        'premium_users': premium_users,
    }
    return render(request, 'users/user_stats.html', context)
