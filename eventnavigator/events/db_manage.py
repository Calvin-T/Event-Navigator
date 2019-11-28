from django.db import connection
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render
from django.core.serializers import serialize

from geojson import Point, Feature, FeatureCollection
import json
from .models import *

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
