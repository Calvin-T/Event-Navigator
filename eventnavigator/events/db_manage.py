from django.db import connection
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render
from django.core.serializers import serialize

from geojson import Point, Feature, FeatureCollection
import json
from .models import *

from datetime import datetime

events_table = '`rutgers-app`.events'

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

        print('[DEBUG] db_manage.register_account()')
        print('[DEBUG] inputUsername: {}'.format(inputUsername))
        print('[DEBUG] inputEmail: {}'.format(inputEmail))
        print('[DEBUG] inputPassword: {}'.format(inputPassword))
        print('[DEBUG] inputConfirmPassword: {}'.format(inputConfirmPassword))
        print('[DEBUG] isOrg {}'.format(isOrg))

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
            print('[DEBUG] RETURN: -1 (Password != confirmPassword)')
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
        print('[DEBUG] RETURN: 1')
        return register_results

#RETURNS: dic with 'eventList' and 'featureList'
    # eventList: list of just each events name and host_org
    # geoData: list of the event's geojson for mapbox
#TODO: filtering by orgs, removing events from the past
def get_events(request):
        events = Event.objects.all()
        eventsList = []
        featureList = []
        for event in events:
            temp = {
                'eventName': event.name,
                'eventHostOrg': event.host_org
            }
            eventsList.append(temp)
            tempPoint = Point((float(event.latitude),float(event.longitude)))
            tempProperties = {
                "marker-colorv": "#fb0246",
                "marker-size": "medium",
                "marker-symbol": "",
                "EventName": event.name,
                "Host Org": event.host_org,
                "Time": event.date.strftime("%m%d%Y, %H:%M")
            }
            tempFeature = Feature(geometry=tempPoint, properties=tempProperties)
            featureList.append(tempFeature)
        geoData = FeatureCollection(featureList)
        print(geoData)

        return {
            'eventList': eventsList,
            'geoData': geoData
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
