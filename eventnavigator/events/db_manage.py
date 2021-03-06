from django.db import connection
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render
from django.core.serializers import serialize

from django.contrib.auth.models import User

from geojson import Point, Feature, FeatureCollection
import json
from .models import *

from datetime import datetime , timedelta
from email.utils import parsedate_tz, mktime_tz

# RETURNS: dict containing 'status' and 'default_field_values'. Called when the user wants to resigister an new accout in register.html
    # status: results after user attempt to register (succss/fail)
    # default_field_values: only if 'status' = error,used to populate registration from
    #                       last attempted registration
def register_account(request):
        inputUsername = request.POST.get("inputUsername")
        inputEmail = request.POST.get("inputEmail")
        inputPassword = request.POST.get("inputPassword")
        inputConfirmPassword = request.POST.get("inputConfirmPassword")
        isOrg = True if request.POST.get("isOrg") == "on" else False

        orgName = request.POST.get("orgName")
        orgLocation = request.POST.get("orgLocation")
        orgWebsite = request.POST.get("orgWebsite")
        orgDescription = request.POST.get("description")

        if inputPassword != inputConfirmPassword:
            messages.error(request,'Error: Passwords do not match! Please try again')
            register_results = {
                'status': "error",
                'default_field_values': {
                        'defaultUsername': inputUsername,
                        'defaultEmail': inputEmail,
                        'defaultIsOrg': isOrg
                    }
            }
            return register_results

        if Account.objects.filter(Q(username=inputUsername) | Q(email=inputEmail)).count() > 0:
            messages.error(request,'Error: username/email already exists! Please try again')
            register_results = {
                'status': "error",
                'default_field_values': {
                        'defaultUsername': inputUsername,
                        'defaultEmail': inputEmail,
                        'defaultIsOrg': isOrg
                    }
            }
            print('[DEBUG] RETURN: -1 (Username/Email exists)')
            return register_results

        if isOrg:
            if Organization.objects.filter(name=orgName).count() > 0:
                messages.error(request,'Error: Organization already exists! Please try again')
                register_results = {
                    'status': "error",
                    'default_field_values': {
                            'defaultUsername': inputUsername,
                            'defaultEmail': inputEmail,
                            'defaultIsOrg': isOrg
                        }
                }
                print('[DEBUG] RETURN: -1 (Username/Email exists)')
                return register_results
            try:
                image = request.FILES["image"]
            except:
                image = None

        #inserting new account into db
        account = Account(username=inputUsername,password=inputPassword,email=inputEmail,isOrg=isOrg)
        account.save()
        if isOrg:
            userID = account.id
            org = Organization(name=orgName,location=orgLocation,website=orgWebsite,description=orgDescription,ownerID=userID,image=image)
            org.save()

        user = User.objects.create_user(inputUsername, inputEmail, inputPassword)
        user.save()
        register_results = {
            'status': "success"
        }
        return register_results

#RETURNS: dic with 'eventList' and 'featureList', supports filtering by dates and org
    # eventList: list of just each events name and host_org
    # geoData: list of the event's geojson for mapbox
# Called by home.html
def get_events(request):
        filter_start_date = request.POST.get("filter_start_date")
        filter_end_date = request.POST.get("filter_end_date")
        filter_org = request.POST.get("filter_org")

        if filter_start_date == None or filter_start_date == '':
            filter_start_date = datetime.today().strftime('%Y-%m-%d')
            filter_end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        if filter_start_date == None or filter_start_date == '':
            temp_sd = datetime.strptime(filter_start_date, '%Y-%m-%d')
            filter_end_date = (temp_sd + timedelta(days=7)).strftime('%Y-%m-%d')
        sd = datetime.strptime(filter_start_date, '%Y-%m-%d')
        ed = datetime.strptime(filter_end_date, '%Y-%m-%d')
        events = ""

        if filter_org == None or filter_org == "":
            events = Event.objects.filter(date__range=[sd,ed]);
            filter_org = ""
        else:
            events =  Event.objects.filter(Q(date__range=[sd,ed]) & Q(host_org = filter_org));
        eventsList = []
        featureList = []
        for event in events:
            temp = {
                'eventID': event.id,
                'eventName': event.name,
                'eventHostOrg': event.host_org,
                'eventDate': event.date.strftime("%m-%d-%Y, %H:%M")
            }
            eventsList.append(temp)
            tempPoint = Point((float(event.longitude),float(event.latitude)))
            tempProperties = {
                "location": event.location,
                "eventName": event.name,
                "hostOrg": event.host_org,
                "date": event.date.strftime("%m-%d-%Y, %H:%M"),
                "eventID": event.id
            }
            tempFeature = Feature(geometry=tempPoint, properties=tempProperties)
            featureList.append(tempFeature)
        geoData = FeatureCollection(featureList)

        return {
            'eventList': eventsList,
            'geoData': geoData,
            'filterDefaults': {
                        'start': filter_start_date,
                        'end': filter_end_date,
                        'org': filter_org
            }
        }
# called by organizations.html
# returns a list of all orgs from db
def get_orgs(request):
        organizations = Organization.objects.all()
        organizationList = []
        for organization in organizations:
            temp = {
                'orgName': organization.name,
                'orgLoc': organization.location,
                'orgWebsite': organization.website,
                'orgDescription': organization.description
            }
            organizationList.append(temp)
        return {
            'organizationList': organizationList
        }
# receives event input from add-event.html and adds it to db
def post_new_event(request):
    eventName = request.POST.get("event_name")
    location = request.POST.get("location")
    room = request.POST.get("room")
    date = request.POST.get("date")
    start_time = request.POST.get("start_time")
    end_time = request.POST.get("end_time")
    lat = request.POST.get("latitude")
    long = request.POST.get("longitude")
    description = request.POST.get("description")
    link = request.POST.get("link")
    try:
        image = request.FILES["image"]
    except:
        image = None
    print(image)

    # Convert 12 hour time into 24 hour time then into time object
    in_time = datetime.strptime(start_time, "%I:%M %p")
    out_time = datetime.strftime(in_time, "%H:%M")
    time_object = datetime.strptime(out_time, '%H:%M').time()

    # Convert date string into date object
    date_object = datetime.strptime(date, '%m/%d/%Y').date()

    # Combine time and date to suitable format for database
    dt = datetime.combine(date_object, time_object)

    # Do same for end time
    in_time = datetime.strptime(end_time, "%I:%M %p")
    out_time = datetime.strftime(in_time, "%H:%M")
    time_object = datetime.strptime(out_time, '%H:%M').time()

    dt2 = datetime.combine(date_object, time_object)

    # Throw error checking cases here
    # start time later than end time
    if dt > dt2:
        print("START TIME > END TIME")
        create_event_results = {
            'status': "error",
            'message': "Start time later than end time."
        }
        return create_event_results

    # Get org
    user = Account.objects.filter(username=request.user.username).first()
    org_object = Organization.objects.filter(ownerID=user.id).first()
    organization = org_object.name

    if Event.objects.filter(Q(name=eventName) and Q(organization=organization) and Q(date=dt)).count() > 0:
        print("DUPLICATE EVENT")
        create_event_results = {
            'status': "error",
            'message': "Event already exists!"
        }
        return create_event_results

    event = Event(name=eventName, date=dt, end_date=dt2, host_org=organization, description=description, longitude=long, latitude=lat, location=location, room=room, image=image, link=link)
    event.save()
    create_event_results = {
        'status': "success"
    }
    print('[DEBUG] RETURN: 1')
    return create_event_results

# Used when user enters the org_detais page.
# RETURNS: a dict containing 'org_info' and 'org_events'
#       'org_info' = dict of the organization's information
#       'org_events' = list of dics of the org's events
def populate_org_details(request):
    org_name = request.GET.get("hostOrg")
    org = Organization.objects.filter(name=org_name).first()
    org_info_dict = {
            'orgName': org_name,
            'orgLocation': org.location,
            'orgDescription': org.description,
            'orgWebsite': org.website,
            'image': org.image
    }
    events = Event.objects.filter(host_org=org_name)
    eventsList = []
    for event in events:
        temp = {
            'eventID': event.id,
            'eventName': event.name,
            'eventDescription': event.description,
            'eventLocation': event.location,
            'eventDate': event.date
        }
        eventsList.append(temp)
    return{
        'org_info': org_info_dict,
        'org_events': eventsList
    }

# RETURNS: a dict of the event information from inputed eventID
def get_event_details(id):
        event = Event.objects.filter(id=id).first()
        event_info_dict = {
            'name': event.name,
            'org' : event.host_org,
            'description': event.description,
            'location': event.location,
            'room': event.room,
            'start_date': event.date,
            'end_date': event.end_date,
            'long': event.longitude,
            'lat': event.latitude,
            'image': event.image,
            'link': event.link,
            'id': id
        }

        return event_info_dict
# used to update the event info based on eventID
# called by edit-event.html
def update_event_details(request, id):
    event = Event.objects.filter(id=id).first()

    event.name = request.POST.get("event_name")
    event.location = request.POST.get("location")
    event.room = request.POST.get("room")
    event.latitude = request.POST.get("latitude")
    event.longitude = request.POST.get("longitude")
    event.description = request.POST.get("description")
    event.link = request.POST.get("link")
    try:
        image = request.FILES["image"]
        event.image = image
    except:
        image = None

    date = request.POST.get("date")
    start_time = request.POST.get("start_time")
    end_time = request.POST.get("end_time")
    # Convert 12 hour time into 24 hour time then into time object
    in_time = datetime.strptime(start_time, "%I:%M %p")
    out_time = datetime.strftime(in_time, "%H:%M")
    time_object = datetime.strptime(out_time, '%H:%M').time()

    # Convert date string into date object
    date_object = datetime.strptime(date, '%m/%d/%Y').date()

    # Combine time and date to suitable format for database
    dt = datetime.combine(date_object, time_object)

    # Do same for end time
    in_time = datetime.strptime(end_time, "%I:%M %p")
    out_time = datetime.strftime(in_time, "%H:%M")
    time_object = datetime.strptime(out_time, '%H:%M').time()

    dt2 = datetime.combine(date_object, time_object)

    if dt > dt2:
        print("START TIME > END TIME")
        create_event_results = {
            'status': "error",
            'message': "Start time later than end time."
        }
        return create_event_results


    event.date = dt
    event.end_date = dt2

    if Event.objects.filter(Q(name=event.name) and Q(organization=event.host_org) and Q(date=dt)).exclude(id=id).count() > 0:
        print("DUPLICATE EVENT")
        create_event_results = {
            'status': "error",
            'message': "Event already exists!"
        }
        return create_event_results


    event.save()
    create_event_results = {
        'status': "success"
    }
    return create_event_results

# Check is a username is an organization
def checkIfOrg(username):
    user = Account.objects.filter(username=username).first()
    if user != None:
        if(user.isOrg == 1):
            return (True, user.id)
        else:
            return (False, user.id)
    else:
        return (False,-1)

# Get org from userID if the account is an org
def getOrgFromOwnerID(id):
    org = Organization.objects.filter(ownerID=id).first()
    print(org)
    org_info_dict = {
            'orgName': org.name,
            'orgLocation': org.location,
            'orgDescription': org.description,
            'orgWebsite': org.website,
            'image': org.image
    }
    return org_info_dict

# Used to update target account in db
def update_account_details(request):
    authID = request.POST.get("authID")
    authUser = User.objects.get(id=authID)

    userID = request.POST.get("userID")
    user = Account.objects.get(id=userID)

    username = request.POST.get("inputUsername")
    email = request.POST.get("inputEmail")

    if Account.objects.filter(Q(username=username) or Q(email=email)).exclude(id=userID).count() > 0:
        update_account = {
            'status': "error",
            'message': "Username or email already exists!"
        }
        return update_account

    authUser.username = username
    authUser.email = email
    authUser.save()

    old_username = user.username

    user.username = username
    user.email = email
    user.save()

    print(user.username)

    isOrg = checkIfOrg(user.username)

    if isOrg[0]:
        org = Organization.objects.get(ownerID=userID)
        if Organization.objects.filter(Q(name=request.POST.get("orgName"))).exclude(ownerID=userID).count() > 0:
            update_account = {
                'status': "error",
                'message': "Org name already exists!"
            }
            return update_account
        events = Event.objects.filter(host_org=org.name)
        for event in events:
            event.host_org = request.POST.get("orgName")
            event.save()
        Organization.objects.filter(ownerID=userID).delete()
        try:
            image = request.FILES["image"]
        except:
            image = None
        print("IMAGE")
        print(image)
        org = Organization(name=request.POST.get("orgName"), location=request.POST.get("orgLocation"),website=request.POST.get("orgWebsite"),description=request.POST.get("description"),ownerID=userID, image=image)
        org.save()
        update_account = {
            'status': "success",
            'message': "Successfully updated!"
        }
        return update_account
        # org.name = request.POST.get("orgName")
        # org.location = request.POST.get("orgLocation")
        # org.website = request.POST.get("orgWebsite")
        # org.description = request.POST.get("description")
        # org.save()

# returns list of comments from an events page. Also posts any comments if sumbitted to event-details.html
def load_n_post_comments(request):
    eventID = request.POST.get('eventID')
    if request.POST.get('commentSubmit') == 'true':
        body = request.POST.get('comment')
        if not isNullOrWhiteSpace(body):
            user_name = request.user.username
            userId = ""
            print("username : {}".format(user_name))
            if not user_name:
                user_name = "USERNAME_NOT_SET"
                userId = 1
            else:
                row = Account.objects.filter(username=user_name)[0]
                userId = row.id
            now = datetime.utcnow()
            comment = Comments(name=user_name,userID=userId,body=body,created=now,eventID=eventID)
            comment.save()

    comments = Comments.objects.filter(eventID=eventID)
    comments_list = []
    for comment in comments:
        username=  Account.objects.filter(id=comment.userID)[0].username
        temp = {
            'body': comment.body,
            'time': comment.created.strftime("%b-%d-%Y (%H:%M)"),
            'username':username
        }
        comments_list.append(temp)
    print(comments_list)
    return comments_list

#"""Indicates whether the specified string is null or empty string.
#   Returns: True if the str parameter is null, an empty string ("") or contains
#   whitespace. Returns false otherwise."""
def isNullOrWhiteSpace(str):
  if (str is None) or (str == "") or (str.isspace()):
    return True
  return False
