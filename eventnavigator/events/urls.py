from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='events-home'),
    path('login', views.login, name='events-login'),
    path('register', views.register, name='events-register'),
    path('organizations', views.organizations, name='events-organizations'),

]
