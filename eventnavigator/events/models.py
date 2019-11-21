from django.db import models

class Event(models.Model):
     name = models.CharField( max_length=60)
     date = models.DateTimeField()
     end_date = models.DateTimeField()
     host_org = models.CharField(max_length=120)
     description = models.CharField(max_length = 1000)
     longitude = models.DecimalField(max_digits=11, decimal_places = 8)
     latitude = models.DecimalField(max_digits=10, decimal_places = 8)
     location = models.CharField(max_length=120)
     room = models.CharField(max_length=20)

class Account(models.Model):
    username = models.CharField(max_length=10)
    password = models.CharField(max_length=128)
    email = models.CharField(max_length=128)
    isOrg = models.BooleanField()

class Organization(models.Model):
    name = models.CharField(primary_key = True, max_length = 20)
    location = models.CharField(max_length = 10)
    description = models.CharField(max_length = 1000)
    website = models.CharField(max_length = 200)
    ownerID = models.IntegerField()
