from django.contrib import admin

# Register your models here.



from django.contrib import admin
from business.models import Business,BusinessAdmin

# Register your models here.
from django.contrib.auth import get_user_model

admin.site.register(Business, BusinessAdmin)