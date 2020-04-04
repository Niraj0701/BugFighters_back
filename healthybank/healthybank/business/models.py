# from django.db import models
#
# Create your models here.
from django.contrib.gis.db import models

from django.contrib import admin

class BusinessAdmin(admin.ModelAdmin):
    search_fields = ['name', 'loc', 'users_allowed', 'slot_size_min']

class Business(models.Model):
    BUSINESS_TYPES = [
        ("UNKNOWN","UNKNOWN"),
        ("BANKE", 'BANKE'),
        ("GROCERY", 'GROCERY'),
        ("PHARMACY", 'PHARMACY'),

    ]

    name = models.CharField(max_length=100)
    loc = models.PointField()
    users_allowed=models.IntegerField(default=10)
    slot_size_min=models.IntegerField(default=15)
    business_type = models.CharField( max_length=20, choices=BUSINESS_TYPES, default="UNKNOWN")

    # timezone = models.

class Slot(models.Model):
      business =  models.ForeignKey('Business', on_delete=models.CASCADE)
      min_time = models.CharField(max_length=100)



