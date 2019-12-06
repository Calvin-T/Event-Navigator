from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.utils.safestring import mark_safe
from django.contrib import messages
from .db_manage import *
import datetime

@csrf_exempt
def home(request):
    events = get_events(request);
    return render(request, 'home.html', {'events': events['eventList'], 'geoData': events['geoData'], 'filterDefaults': events['filterDefaults']})

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
    id = request.GET.get("eventID")
    print(id)
    event = get_event_details(id)
    long = event['long']
    lat = event['lat']
    link = "https://api.mapbox.com/v4/mapbox.streets/pin-m-marker+285A98({},{})/{},{},15/600x300@2x.png?access_token=pk.eyJ1IjoiY3RhbmcxOTk4IiwiYSI6ImNrMm10MXl2YjBsZmIzbXQ1NW15YW15OTIifQ.tethu75zoCk5OiHARIYZ9A".format(long, lat, long, lat)
    print(link)
    image = event['image']
    print(image)
    hasImage = True
    if image == '':
        hasImage = False
    return render(request, 'event-detail.html', {'event': event , 'map_link': link, 'hasImage': hasImage})

def org_details(request):
    if request.method == 'GET':
        print('GET')
        populator = populate_org_details(request)
        return render(request, 'org-detail.html', {'info': populator['org_info'], 'events': populator['org_events']})
    else:
        id = request.POST.get('eventID')
        Event.objects.filter(id=id).delete()
        print("DELETED EVENT")
        populator = populate_org_details(request)
        return render(request, 'org-detail.html', {'info': populator['org_info'], 'events': populator['org_events']})


def add_event(request):
    if request.method == 'POST':
        print("POST")
        create_event_results = post_new_event(request)
        if create_event_results['status'] == "error":
            messages.error(request, create_event_results['message'])
            return render(request, 'add-event.html')
        else:
            messages.success(request, 'Successfully created new event!')
            return render(request, 'add-event.html')
    return render(request, 'add-event.html')

def edit_account(request):
    return render(request, 'edit-account.html')

def edit_event(request):
    if request.method == 'POST':
        id = request.POST.get('eventID')
        print(id)
        result = update_event_details(request, id)
        if result['status'] == "success":
            messages.success(request, 'Successfully updated event!')
            return render(request, 'event-detail.html')
        return render(request, 'home.html')
    else:
        id = request.GET.get('eventID')
        print("ID: " + id)
        event = get_event_details(id)
        image = event['image']
        #start_date = event['start_date'].date()
        start_time = event['start_date'].time()
        end_time = event['end_date'].time()
        start_date = datetime.date.strftime(event['start_date'].date(), "%m/%d/%y")

        hasImage = True
        if image == '':
            hasImage = False
        return render(request, 'edit-event.html', {'event': event, 'id': id,'hasImage': hasImage, 'date': start_date, 'start_time':start_time, 'end_time': end_time})
