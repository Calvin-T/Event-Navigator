from django.db import connection
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render
from .models import *

events_table = '`rutgers-app`.events'

# RETURN VALUES:
#   -1 = Unsucessful attempt (username/email already exist, or PW != confirmPW)
#   1 = account successfully created within function
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

        if Account.objects.filter(Q(username=inputUsername) | Q(email=inputUsername)).count() > 0:
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

#Returns ALL evenets in db.
#TODO: filtering by orgs, removing events from past
def get_events(request):
        events = Event.objects.all()
        eventsList = []
        for event in events:
            temp = {
                'eventName': event.name,
                'eventHostOrg': event.host_org
            }
            eventsList.append(temp)
        return eventsList
