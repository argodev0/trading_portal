from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Welcome to Trading Portal - Users App is working!")

def home(request):
    return render(request, 'users/home.html')
