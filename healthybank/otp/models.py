from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
from healthybank import settings
from commons.models import BaseModel


class OTP(BaseModel):
    OTP_CHOICES = (
        ("VERIFICATION", "Verification otp"),
        ("PAYMENT", "Payment otp"),
        ('PASSWORD_UPDATE','Password Update Otp')

    )
    user = models.ForeignKey(get_user_model(), related_name="otps", on_delete=models.CASCADE)
    otp = models.IntegerField(null=False)
    purpose = models.CharField(max_length=20, default="LOGIN", choices=OTP_CHOICES)


    def is_valid(self, otp, purpose):
        from datetime import datetime
        elapsedTime = (int)(datetime.now().timestamp() - self.updated_at.timestamp())
        if elapsedTime > settings.OTP_MAX_TIME or otp != self.otp or purpose != self.purpose:
            print("INVALID USER")
            return False

        return True

    def __str__(self):
        return "%s : %s" % (self.user.name, self.purpose)

from django.contrib import admin

class OTPAdmin(admin.ModelAdmin):
    search_fields = ['user']
