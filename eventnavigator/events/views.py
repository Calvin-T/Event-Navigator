from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.utils.safestring import mark_safe
from django.contrib import messages
from .db_manage import *
import datetime
from .forms import CommentForm

@csrf_exempt
def home(request):
    events = get_events(request);
    org = {}
    hasOrg = False
    if request.user.is_authenticated:
        print("Logged in HOME")
        isOrg = checkIfOrg(request.user.username)
        if isOrg[0]:
            print(isOrg[1])
            hasOrg = True
            org = getOrgFromOwnerID(isOrg[1])
    else:
        print("Not logged in HOME")
    return render(request, 'home.html', {'events': events['eventList'], 'geoData': events['geoData'], 'filterDefaults': events['filterDefaults'], 'org':org, 'hasOrg':hasOrg})

def organizations(request):
    if request.user.is_authenticated:
        print("Logged in ORGS")
        print(request.user.username)
        isOrg = checkIfOrg(request.user.username)
    else:
        print("Not logged in ORGS")
        isOrg = [False]
    if request.method == 'GET':
        organizations = get_orgs(request);
    return render(request, 'organizations.html',  {'organizations': organizations['organizationList'], 'isOrg': isOrg[0]})


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
            return redirect('events-login')
    return render(request, 'register.html')

@csrf_exempt
def event_details(request):
    loggedin = 'false'
    if request.user.is_authenticated:
        loggedin = 'true'
        print(request.user.username)
        isOrg = checkIfOrg(request.user.username)
    else:
        print("Not logged in EVENT D")
    id = request.POST.get("eventID")
    isOrg = [False]
    if not id:
        return home(request)

    event = get_event_details(id)
    long = event['long']
    lat = event['lat']
    link = "https://api.mapbox.com/v4/mapbox.streets/pin-m-marker+285A98({},{})/{},{},15/600x300@2x.png?access_token=pk.eyJ1IjoiY3RhbmcxOTk4IiwiYSI6ImNrMm10MXl2YjBsZmIzbXQ1NW15YW15OTIifQ.tethu75zoCk5OiHARIYZ9A".format(long, lat, long, lat)
    #print(link)
    image = event['image']
    #print(image)
    hasImage = True
    if image == '':
        hasImage = False
    comments = load_n_post_comments(request)
    return render(request, 'event-detail.html', {'event': event , 'map_link': link, 'hasImage': hasImage, 'loggedin':loggedin, 'comments': comments, 'isOrg': isOrg[0]})


def org_details(request):
    if request.user.is_authenticated:
        print("Logged in ORG D")
        print(request.user.username)
    else:
        print("Not logged in ORG D")
        isOrg = [False]
    if request.method == 'GET':
        isOwner = False
        if request.user.is_authenticated:
            isOrg = checkIfOrg(request.user.username)
            if isOrg[0]:
                # Check if it is signed in users org
                user = Account.objects.filter(username=request.user.username).first()
                user_org = getOrgFromOwnerID(user.id)
                org_name = request.GET.get("hostOrg")
                print(user_org)
                print(org_name)
                if user_org['orgName'] == org_name:
                    isOwner = True
        populator = populate_org_details(request)
        image = populator['org_info']['image']
        hasImage = True
        if image == '':
            hasImage = False
        return render(request, 'org-detail.html', {'info': populator['org_info'], 'events': populator['org_events'], 'isOwner': isOwner, 'isOrg':isOrg[0],'hasImage': hasImage})
    else:
        id = request.POST.get('eventID')
        Event.objects.filter(id=id).delete()
        print("DELETED EVENT")
        if request.user.is_authenticated:
            isOrg = checkIfOrg(request.user.username)
            if isOrg[0]:
                # Check if it is signed in users org
                user = Account.objects.filter(username=request.user.username).first()
                user_org = getOrgFromOwnerID(user.id)
                org_name = request.GET.get("hostOrg")
                print(user_org['orgName'])
                print(org_name)
                if user_org['orgName'] == org_name:
                    isOwner = True
        populator = populate_org_details(request)
        image = populator['org_info']['image']
        hasImage = True
        if image == '':
            hasImage = False
        return render(request, 'org-detail.html', {'info': populator['org_info'], 'events': populator['org_events'],'isOwner': isOwner, 'isOrg':isOrg[0],'hasImage': hasImage})


def add_event(request):
    if request.user.is_authenticated:
        print("Logged in ADD E")
        print(request.user.username)
        isOrg = checkIfOrg(request.user.username)
    else:
        print("Not logged in ADD E")
        isOrg = [False]
    if request.method == 'POST':
        print("POST")
        create_event_results = post_new_event(request)
        if create_event_results['status'] == "error":
            messages.error(request, create_event_results['message'])
            return render(request, 'add-event.html',{'isOrg':isOrg[0]})
        else:
            messages.success(request, 'Successfully created new event!')
            return render(request, 'add-event.html',{'isOrg':isOrg[0]})
    return render(request, 'add-event.html',{'isOrg':isOrg[0]})

def edit_event(request):
    if request.user.is_authenticated:
        print("Logged in E E")
        print(request.user.username)
    else:
        print("Not logged inE E")
    if request.method == 'POST':
        id = request.POST.get('eventID')
        print(id)
        result = update_event_details(request, id)
        if result['status'] == "success":
            storage = messages.get_messages(request)
            storage.used = True
            messages.success(request, 'Changes saved')
        else:
            storage = messages.get_messages(request)
            storage.used = True
            messages.error(request, 'Duplicate event')
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
    else:
        id = request.GET.get('eventID')
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

def account_details(request):
    if request.user.is_authenticated:
        print("Logged in Account Detail")
        print(request.user.username)
    else:
        print("Not logged in Account Detail")


    username = request.user.username
    email = request.user.email

    user = Account.objects.filter(username=username).first()
    userID = user.id

    authUser = User.objects.get(username = username)
    authID = authUser.id

    isOrg = checkIfOrg(username)
    org = {}
    hasImage = False
    if isOrg[0]:
        org = getOrgFromOwnerID(userID)
        orgImage = org['image']
        if orgImage != '':
            hasImage = True

    return render(request, 'account-detail.html', {'username': username, 'email': email,'isOrg':isOrg[0], 'org':org, 'userID': userID, 'authID': authID, 'hasImage':hasImage})


def edit_account(request):
    if request.user.is_authenticated:
        print("Logged in Edit Acc")
        print(request.user.username)
    else:
        print("Not logged in Edit Acc")

    if request.method == 'GET':
        username = request.GET.get("username")
        email = request.GET.get("email")
        isOrg = checkIfOrg(username)
        orgName = request.GET.get("orgName")
        orgLocation = request.GET.get("orgLocation")
        orgWebsite = request.GET.get("orgWebsite")
        orgDescription = request.GET.get("orgDescription")
        orgImage = request.GET.get("orgImage")
        org = {'orgName': orgName, 'orgLocation': orgLocation, 'orgWebsite': orgWebsite, 'orgDescription': orgDescription, 'image':orgImage}
        hasImage = True
        if orgImage == '':
            hasImage = False
        userID = request.GET.get("userID")
        authID = request.GET.get("authID")

        return render(request, 'edit-account.html', {'username': username, 'email': email,'isOrg':isOrg[0], 'org': org, 'userID': userID, 'authID': authID, 'hasImage': hasImage})
    else:
        result = update_account_details(request)
        if result['status'] == "error":
            messages.error(request, result['message'])
        else:
            messages.success(request, 'Successfully updated!')
        return redirect('events-account-detail')
