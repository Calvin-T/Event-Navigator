from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.utils.safestring import mark_safe
from .db_manage import *

def home(request):
    if request.method == 'GET':
        events = get_events(request);
    return render(request, 'home.html', {'events': events['eventList'], 'geoData': events['geoData']})

def organizations(request):
    if request.method == 'GET':
        organizations = get_orgs(request);
    return render(request, 'organizations.html',  {'organizations': organizations['organizationList']})

def login(request):
    return render(request, 'login.html')

# @csrf_except used for 403 errors on POST request, might need another fix.
# see: https://tinyurl.com/yggzrqb3
@csrf_exempt
def register(request):
    if request.method == 'POST':
        register_results = register_account(request)
        if register_results['status'] == "error":
            return render(request, 'register.html', {'values': mark_safe(register_results['default_field_values'])})
        else:
            #TODO: add register-successful notification once reaching login.html
            return render(request, 'login.html')
    return render(request, 'register.html')

def account_details(request):
    return render(request, 'account-detail.html')

def event_details(request):
    return render(request, 'event-detail.html')

def org_details(request):
    return render(request, 'org-detail.html')

def add_event(request):
    return render(request, 'add-event.html')
