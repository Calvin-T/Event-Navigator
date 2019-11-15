from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from .db_manage import *
from .forms import RegisterForm

def home(request):
    return render(request, 'home.html')

def organizations(request):
    return render(request, 'organizations.html')

def login(request):
    return render(request, 'login.html')

# @csrf_exce1pt used for 403 errors on POST request, might need another fix.
# see: https://tinyurl.com/yggzrqb3
@csrf_exempt
def register(request):
    if request.method == 'POST':
        register_account(request)
    return render(request, 'register.html')

def account_details(request):
    return render(request, 'account-detail.html')

def event_details(request):
    return render(request, 'event-detail.html')

def org_details(request):
    return render(request, 'ord-detail.html')
