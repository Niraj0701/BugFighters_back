from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
from healthybank import settings
from commons.models import BaseModel
import logging
logger = logging.getLogger('otp.models')
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
            logger.debug("either time elapsed or otp didnt match or purpose didnt match")
            logger.debug("Purpose Elapsed Time : %s provided otp %s requested purpose: %s" % ( elapsedTime, otp, purpose))
            return False

        return True

    def __str__(self):
        return "%s : %s" % (self.user.name, self.purpose)

from django.contrib import admin

class OTPAdmin(admin.ModelAdmin):
    search_fields = ['user']
