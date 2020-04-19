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
from rest_framework_simplejwt.exceptions import InvalidToken

from business.models import UserSlot
from users.models import User
from rest_framework.views import APIView
from business.views import BusinessSerializer, UserSlotSerializer

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
        fields = ['name',  'id', 'email', 'verification_state', 'mobile','profile','businesses','password']
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
        userModel.save()
        data = {'user': UserBasicSerializer(userModel, many=False).data}

        return Response(data, status=status.HTTP_200_OK)


class UserSelfProfileAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
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

        date = self.request.query_params.get('date')
        slot = self.request.query_params.get('slot')
        if date is None:
            from datetime import date
            date = date.today().strftime("%Y-%m-%d")
            print("Querying for date %s" % date)
        user = self.get_object()
        print("Requesting query %s %s" % (date, user))

        user_slot_query = UserSlot.objects.filter(user=user)
        if date is not None:
            user_slot_query = user_slot_query.filter(date=date)
        if slot is not None:
            user_slot_query = user_slot_query.filter(slot=slot)
        user_slot_query = user_slot_query.order_by('date','slot')
        return user_slot_query

