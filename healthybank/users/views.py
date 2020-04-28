from tokenize import TokenError

from django.http import Http404
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response

from rest_framework import routers, serializers
from rest_framework import authentication, permissions
from rest_framework import generics, status
import logging
from django.contrib.auth import get_user_model
from healthybank.settings import COUNTRY_CODE_MAPPING_MAP
from rest_framework_simplejwt.exceptions import InvalidToken

from business.models import UserSlot
from otp.views import OTPRequestSerializer
from users.models import User
from rest_framework.views import APIView
from business.views import BusinessSerializer, UserSlotSerializer, SlotFilter

logger = logging.getLogger(__name__)
class UserSerializer(serializers.ModelSerializer):
    # role = serializers.SerializerMethodField('get_role')

    class Meta:
        model = User
        fields = '__all__'
    #
    # def get_role(self, obj):
    #     if obj.employee:
    #         return obj.employee.role
    #     return Employee.ORG_ADMIN


class UserBasicSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()
    email = serializers.EmailField(read_only=False, required=False)
    verification_state = serializers.CharField(read_only=True)
    businesses = BusinessSerializer(many=True,read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name',  'id', 'email', 'verification_state', 'mobile','profile','businesses','password', 'country', 'country_code']
        read_only_fields = ['id']

    # def get_businesses(self,obj):
    #     businesses = obj.business_set.all()
    #
    #     if obj.profile == 'ServiceProvider' and len(businesses) !=0:
    #         return BusinessSerializer
    #     return None
        # if self.profile == "BusinessOwner":


class UserWritableSerializer(serializers.Serializer):
    name = serializers.CharField()
    mobile = serializers.CharField()
    dob = serializers.DateField()

    class Meta:
        model = User
        fields = ['name',  'pan', 'dob']


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
#
class MobileAuthenticationView(TokenObtainPairView):

    class Meta:
        proxy = True

class UsersAPI(generics.ListCreateAPIView):
    serializer_class = UserBasicSerializer
    # def authenticate(self, email=None, password=None, **kwargs):
    #     UserModel = get_user_model()
    #     try:
    #         user = UserModel.objects.get(email=email)
    #         print(user)
    #     except UserModel.DoesNotExist:
    #         return None
    #     else:
    #         if user.check_password(password):
    #             return user
    #     return None

    # class Meta:


    def get_queryset(self):
        return User.objects.all()

    def post(self, request, format=None):
        '''
            Fetch self profile
        '''
        logger.debug("User %s %s", request.user, type(request.user))
        UserModel = get_user_model()
        userModel = UserModel()
        userModel.name =  request.data['name']
        userModel.mobile =  request.data['mobile']
        userModel.profile = request.data['profile']
        userModel.set_password(request.data['password'])
        if 'country' in request.data and request.data['country'] in COUNTRY_CODE_MAPPING_MAP:
            userModel.country = request.data['country']
            userModel.country_code = COUNTRY_CODE_MAPPING_MAP[request.data['country']]['Dial']
        userModel.save()
        data = {'user': UserBasicSerializer(userModel, many=False).data}

        return Response(data, status=status.HTTP_200_OK)

class UserVerificationSerializer(serializers.Serializer):
    otp=serializers.IntegerField(write_only=True,required=True)

class PasswordUpdateSerializer(serializers.Serializer):
    otp = serializers.IntegerField(write_only=True, required=True)
    password = serializers.CharField(max_length=20,write_only=True, required=True)
    confirmed_password = serializers.CharField(max_length=20,write_only=True, required=True)
    mobile = serializers.CharField(max_length=10,write_only=True,required=False)

class UserVerificationAPI(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserVerificationSerializer

    def post(self,request,id,format=None):
        try:
            user = get_user_model().objects.get(id=request.user.id)
            purpose='VERIFICATION'
            if 'purpose' in request.data:
                purpose = request.data['purpose'].upper()
            from otp.models import OTP
            requested_otp = OTP.objects.get(user=user)
            if requested_otp.is_valid(otp=request.data['otp'], purpose = purpose):
                user.verification_state = 'VERIFIED'
                user.save()
                # Change tokens
                return Response(data="USER_VERIFIED", status=status.HTTP_200_OK)
            else:
                return Response(data="INVALID_OTP", status=status.HTTP_200_OK)
        except:
            import traceback
            traceback.print_exc()
            logger.error("Failed to verify user %s " % request.user.id)
        return Response(data="INVALID_USER",status=status.HTTP_404_NOT_FOUND)


from commons.utils import PasswordUpdateThrottle
class UnAuthenticatedPasswordUpdateWithOTPAPI(generics.GenericAPIView):
    serializer_class = PasswordUpdateSerializer
    throttle_scope = 'password'
    def post(self,request,format=None):
        try:
            user = get_user_model().objects.get(mobile=request.data['mobile'])
            from otp.models import OTP
            requested_otp = OTP.objects.get(user=user)
            if request.data['password'] != request.data['confirmed_password']:
                return Response(data="PASSWORD_MISMATCH", status=status.HTTP_401_UNAUTHORIZED)

            if requested_otp.is_valid(otp=request.data['otp'], purpose = 'PASSWORD_UPDATE'):
                user.set_password(request.data['password'])
                user.save()
                return Response(data="PASSWORD_UPDATED", status=status.HTTP_200_OK)
            else:
                return Response(data="INVALID_OTP", status=status.HTTP_401_UNAUTHORIZED)
        except:
            import traceback
            traceback.print_exc()
            logger.error("Failed to verify user %s " % request.user.id)
        return Response(data="INVALID_USER",status=status.HTTP_404_NOT_FOUND)


class AuthenticatedPasswordUpdateWithOTPAPI(generics.GenericAPIView):
    serializer_class = PasswordUpdateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request,format=None):
        try:
            user = get_user_model().objects.get(id=request.user.id)
            from otp.models import OTP
            requested_otp = OTP.objects.get(user=user)
            if request.data['password'] != request.data['confirmed_password']:
                return Response(data="PASSWORD_MISMATCH", status=status.HTTP_401_UNAUTHORIZED)

            if requested_otp.is_valid(otp=request.data['otp'], purpose = 'PASSWORD_UPDATE'):
                user.set_password(request.data['password'])
                user.save()
                return Response(data="PASSWORD_UPDATED", status=status.HTTP_200_OK)
            else:
                return Response(data="INVALID_OTP", status=status.HTTP_401_UNAUTHORIZED)
        except:
            import traceback
            traceback.print_exc()
            logger.error("Failed to verify user %s " % request.user.id)
        return Response(data="INVALID_USER",status=status.HTTP_404_NOT_FOUND)


class UserSelfProfileAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request,id=None, format=None):
        '''
            Fetch self profile
        '''
        logger.debug("User %s %s", request.user, type(request.user))
        UserModel = get_user_model()
        user = UserModel.objects.get(id=request.user.id)

        data = {'user': UserBasicSerializer(user, many=False).data}

        return Response(data, status=status.HTTP_200_OK)



class UserSlots(generics.ListAPIView):
    """
    View to list all users in the system.
    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = []
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (permissions.IsAuthenticated,)
    from business.models import UserSlot
    serializer_class = UserSlotSerializer
    filterset_fields = ['date', 'longitude', 'business_type', "slot"]
    filterset_fields = ['date', 'longitude', 'business_type', "slot"]
    query_params = [{'name': 'slot', 'type': 'string'},
                    {'name': 'date', 'type': 'string', 'description': 'date in format YYYY-mm-dd'},
                    {'name': 'business_type', 'type': 'String'}]
    filter_backends = [SlotFilter]

    def get_object(self):
        try:

            return User.objects.get(id=self.kwargs.get('id'))
        except User.DoesNotExist:
            raise Http404

    def get_queryset(self, id=None):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """

        requested_date = self.request.query_params.get('date')
        slot = self.request.query_params.get('slot')
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")
        if requested_date is None:
            requested_date = today
            print("Querying for date %s" % date)
        user = self.get_object()

        user_slot_query = UserSlot.objects.filter(user=user)
        if date is not None:
            user_slot_query = user_slot_query.filter(date=requested_date)
        if slot is not None:
            user_slot_query = user_slot_query.filter(slot=slot)
        user_slot_query = user_slot_query.order_by('date','slot')
        return user_slot_query

