from django.contrib.auth import get_user_model
from django.shortcuts import render
import logging
import random
# Create your views here.
from rest_framework.generics import GenericAPIView

from rest_framework.response import Response
from rest_framework import serializers, status, permissions
from otp.models import OTP
from datetime import datetime, timedelta
from otp.tasks import otp_generated
logger = logging.getLogger('otp.views')
class OTPRequestSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=10, required=False)
    otp = serializers.IntegerField(required=False)

class RequestOTP(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OTPRequestSerializer

    def get(self, request, format=None):

        try:
            user = get_user_model().objects.get(id=request.user.id)

            otp =  None
            try:
                otp = OTP.objects.get(user=user)
            except:
                otp: None

            if otp is not None:
                logger.debug("%s %s" % ( otp.updated_at, datetime.now()))
                elapsedTime = (int)(datetime.now().timestamp() - otp.updated_at.timestamp())
                if elapsedTime < 300:
                    return Response(data="Request after 5 mins", status=status.HTTP_400_BAD_REQUEST)
            else:
                otp = OTP()
                otp.user = user
                elapsedTime =  None

            if elapsedTime is None or elapsedTime > 300:
                otp.otp = random.randint(100000, 999999)
                otp.save()
                from otp.tasks import otp_generated
                id=otp_generated.apply_async(kwargs={'otp': otp.otp, 'mobile': otp.user.mobile})
                logger.debug("Sent OTP %s" % id)
                return Response( data={"otp" : otp.otp}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Failed to create OTP: %s" % ( e.args))
            import traceback
            traceback.print_exc()

        return Response(status=status.HTTP_400_BAD_REQUEST)




