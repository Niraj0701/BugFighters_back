from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
from commons.models import BaseModel


class OTP(BaseModel):
    OTP_CHOICES = (
        ("VERIFICATION", "Verification otp"),

    )
    user = models.ForeignKey(get_user_model(), related_name="otps", on_delete=models.CASCADE)
    otp = models.IntegerField(null=False)
    purpose = models.CharField(max_length=20, default="LOGIN", choices=OTP_CHOICES)


