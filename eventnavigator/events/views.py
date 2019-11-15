from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, 'home.html')

def organizations(request):
    return render(request, 'organizations.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def account_details(request):
    return render(request, 'account-detail.html')

def event_details(request):
    return render(request, 'event-detail.html')

def org_details(request):
    return render(request, 'org-detail.html')

def add_event(request):
    return render(request, 'add-event.html')
