from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='events-home'),
    path('login', views.login, name='events-login'),
    path('register', views.register, name='events-register'),
    path('organizations', views.organizations, name='events-organizations'),
    path('account-details', views.account_details, name='events-account-detail'),
    path('event-details', views.event_details, name='events-event-details'),
    path('org-details', views.org_details, name='events-org-details'),
    path('add-event', views.add_event, name='events-add-event'),

]
