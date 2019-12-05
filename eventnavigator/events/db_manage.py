from django.db import connection
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render
from django.core.serializers import serialize

from geojson import Point, Feature, FeatureCollection
import json
from .models import *

from datetime import datetime , timedelta
from email.utils import parsedate_tz, mktime_tz

# RETURNS: dict containing 'status' and 'default_field_values'
    # status: results after user attempt to register (succss/fail)
    # default_field_values: only if 'status' = error,used to populate registration from
    #                       last attempted registration
def register_account(request):
        inputUsername = request.POST.get("inputUsername")
        inputEmail = request.POST.get("inputEmail")
        inputPassword = request.POST.get("inputPassword")
        inputConfirmPassword = request.POST.get("inputConfirmPassword")
        isOrg = True if request.POST.get("isOrg") == "on" else False

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
        #inserting new account into db
        account = Account(username=inputUsername,password=inputPassword,email=inputEmail,isOrg=isOrg)
        account.save()
        register_results = {
            'status': "success"
        }
        return register_results

#RETURNS: dic with 'eventList' and 'featureList', supports filtering by dates and org
    # eventList: list of just each events name and host_org
    # geoData: list of the event's geojson for mapbox
#TODO: removing events from the past
def get_events(request):
        filter_start_date = request.POST.get("filter_start_date")
        filter_end_date = request.POST.get("filter_end_date")
        filter_org = request.POST.get("filter_org")

        if filter_start_date == None:
            filter_start_date = datetime.today().strftime('%Y-%m-%d')
            filter_end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        sd = datetime.strptime(filter_start_date, '%Y-%m-%d')
        ed = datetime.strptime(filter_end_date, '%Y-%m-%d')
        events = ""

        if filter_org == None:
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
                'eventHostOrg': event.host_org
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

def get_orgs(request):
        organizations = Organization.objects.all()
        organizationList = []
        for organization in organizations:
            temp = {
                'orgName': organization.name,
                'orgLoc': organization.location
            }
            organizationList.append(temp)
        return {
            'organizationList': organizationList
        }

def post_new_event(request):
    eventName = request.POST.get("event_name")
    organization = request.POST.get("organization")
    location = request.POST.get("location")
    room = request.POST.get("room")
    date = request.POST.get("date")
    start_time = request.POST.get("start_time")
    end_time = request.POST.get("end_time")
    lat = request.POST.get("latitude")
    long = request.POST.get("longitude")
    description = request.POST.get("description")

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

    if Event.objects.filter(Q(name=eventName) and Q(organization=organization) and Q(date=dt)).count() > 0:
        print("DUPLICATE EVENT")
        create_event_results = {
            'status': "error",
            'message': "Event already exists!"
        }
        return create_event_results

    event = Event(name=eventName, date=dt, end_date=dt2, host_org=organization, description=description, longitude=long, latitude=lat, location=location, room=room)
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
            'orgWebsite': org.website
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
