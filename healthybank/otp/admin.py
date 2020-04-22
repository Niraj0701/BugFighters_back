from django.contrib import admin

# Register your models here.


from django.contrib import admin

# Register your models here.
from otp.models import OTP,OTPAdmin
admin.site.register(OTP, OTPAdmin)


