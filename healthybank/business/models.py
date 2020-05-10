# from django.db import models
#
# Create your models here.
from django.contrib.gis.db import models

from django.contrib import admin
from django import forms

from mapwidgets.widgets import GooglePointFieldWidget, GoogleStaticOverlayMapWidget
from django.contrib.auth import get_user_model

from healthybank.settings import BUSINESS_TYPES


class BusinessAdmin(admin.ModelAdmin):
    search_fields = ['name', 'loc', 'users_allowed', 'slot_size_min']
    formfield_overrides = {
        models.PointField: {"widget": GooglePointFieldWidget}
    }

class UserslotAdmin(admin.ModelAdmin):
        search_fields = ['business', 'customer_name', 'mobile', 'slot',"date"]

class Business(models.Model):


    name = models.CharField(max_length=100)
    loc = models.PointField()
    users_allowed=models.IntegerField(default=10)
    slot_size_min=models.IntegerField(default=15)
    business_type = models.CharField( max_length=20, choices=BUSINESS_TYPES, default="UNKNOWN")
    start_time=models.TimeField(default="9:00")
    end_time = models.TimeField(default="17:00")
    address = models.TextField(max_length=100, null=True,default=None)
    manager =  models.ForeignKey(get_user_model(), related_name='businesses', null=False, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


    @property
    def slots(self):
        print(self.start_time,self.end_time)

        start_hr,start_min =  str(self.start_time).split(":")[:2]
        end_hr, end_min = str(self.end_time).split(":")[:2]
        start_min_of_day = int(start_hr) * 60 + int(start_min)
        end_min_of_day = int(end_hr)*60+int(end_min)
        slots = []
        slot_start = start_min_of_day
        while slot_start < end_min_of_day:
            slots.append('{:02d}:{:02d}'.format(*divmod(slot_start, 60)))
            slot_start += int(self.slot_size_min)
        return slots

class BusinessForm(forms.ModelForm):
        class Meta:
            model = Business
            fields = ("name","loc")
            widgets = {
                'loc': GooglePointFieldWidget,
                # 'city_hall': GoogleStaticOverlayMapWidget,
            }
    # timezone = models.

class UserSlot(models.Model):
      business =  models.ForeignKey('Business', on_delete=models.CASCADE)
      slot = models.CharField(max_length=100)
      user =  models.ForeignKey('users.User', related_name="slots", on_delete=models.CASCADE, null=True)
      comments = models.TextField(max_length=10000, null=True)
      # customer_name =models.CharField(max_length=100,default=None)
      # mobile = models.CharField(max_length=10,default="9766818825", null=True, blank=True )
      # user = models.ForeignKey(User)
      date = models.DateField()

      def __str__(self):
          return "%s %s @ %s" %  ( self.user.name, self.user.mobile ,self.business.name )



