from django.urls import path
from django.contrib.auth import views as authviews
from . import views

urlpatterns = [

    path('', views.home, name='events-home'),
    path('login', authviews.LoginView.as_view(), name='events-login'),
    path('logout', authviews.LogoutView.as_view(), name='events-logout'),
    path('register', views.register, name='events-register'),
    path('organizations', views.organizations, name='events-organizations'),
    path('account-details', views.account_details, name='events-account-detail'),
    path('event-details', views.event_details, name='events-event-details'),
    path('org-details', views.org_details, name='events-org-details'),
    path('add-event', views.add_event, name='events-add-event'),
    path('edit-account', views.edit_account, name='events-edit-account'),
    path('edit-event', views.edit_event, name='events-edit-event'),

]
