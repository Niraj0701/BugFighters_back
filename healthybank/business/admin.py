from django.contrib import admin

# Register your models here.



from django.contrib import admin
from business.models import Business,BusinessAdmin
from business.models import UserSlot,UserslotAdmin
# Register your models here.
from django.contrib.auth import get_user_model

admin.site.register(Business, BusinessAdmin)
admin.site.register(UserSlot, UserslotAdmin)