from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response

from rest_framework import routers, serializers
from rest_framework import authentication, permissions
from rest_framework import generics, status
import logging
from django.contrib.auth import get_user_model
from users.models import User
from rest_framework.views import APIView

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
    email = serializers.EmailField(read_only=False)
    verification_state = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'id', 'email', 'verification_state', 'mobile']
        read_only_fields = ['id']



class UserWritableSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    mobile = serializers.CharField()
    dob = serializers.DateField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'pan', 'dob']


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

class MobileAuthenticationView(TokenObtainPairView):
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