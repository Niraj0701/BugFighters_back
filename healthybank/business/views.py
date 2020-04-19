# Create your views here.
import coreschema
from django.contrib.gis.db.models.functions import Distance
from django.http import Http404
from rest_framework import serializers
from rest_framework.schemas import ManualSchema

from business.models import Business, UserSlot
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
import logging
from django.contrib.gis.geos import *
from rest_framework import authentication, permissions


logger = logging.getLogger(__name__)
from django_filters.rest_framework import DjangoFilterBackend


class BusinessSerializer(serializers.ModelSerializer):
    coords = serializers.SerializerMethodField('get_coords', read_only=False)
    # slots = serializers.SerializerMethodField('get_slots', read_only=True)
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    distance = serializers.DecimalField(
        source='distance.m', max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = Business
        fields = ['name', 'coords', 'id', "business_type", 'users_allowed', 'slot_size_min', "longitude", "latitude",
                  "slots", "start_time", "end_time", "address", "distance"]
        # exclude = ['organization']
        # fields = '__all__'

    def get_coords(self, obj):
        if isinstance(obj, Business):
            return {"longitude": obj.loc.x, "latitude": obj.loc.y}
        return {}

    # def get_distance(self,obj):
    #
    #     latitude = self.context['request'].query_params.get('latitude')
    #     longitude = self.context['request'].query_params.get('longitude')
    #     if latitude is not None and longitude is not None:
    #         request_location = GEOSGeometry('SRID=4326;POINT(%s %s)' % ( latitude, longitude))
    #
    #         return obj.loc.distance(request_location) * 100 * 1000
    #     return 0



class UserSlotSerializer(serializers.ModelSerializer):
    business = serializers.SerializerMethodField('get_business', read_only=True)
    date = serializers.DateField(required=False)
    user = serializers.SerializerMethodField('get_user', read_only=True)

    class Meta:
        model = UserSlot
        fields = '__all__'
        excludes = ['user']

    def get_business(self, obj):
        if isinstance(obj, UserSlot):
            return {"name": obj.business.name, "id": obj.business.id, "type": obj.business.business_type}
        return {}
    def get_user(self,obj):
        return {"name":obj.user.name, "mobile": obj.user.mobile}
    
from drf_yasg.utils import swagger_auto_schema

from drf_yasg.inspectors import SwaggerAutoSchema
from inflection import camelize

from rest_framework.filters import BaseFilterBackend
import coreapi
from rest_framework import filters
class QueryParamBasedFilter(filters.BaseFilterBackend):
    def get_search_fields(self, view, request):
        """
        Search fields are obtained from the view, but the request is always
        passed to this method. Sub-classes can override this method to
        dynamically change the search fields based on request content.
        """
        return getattr(view, 'query_params', None)

    def get_schema_fields(self, view):
        sf_result = self.get_search_fields(view, None)

        print(sf_result)
        results = []
        i =0
        for field in sf_result:

            newField = None
            if field['type'].upper() =='float'.upper():
                newField = coreapi.Field(
                    name=field['name'],
                    required=False, location='query',
                    schema=coreschema.Number(
                        title=field['name'],
                        description=field['description'] if 'description' in field else None
                    )
                )
            elif field['type'].upper =='int'.upper():
                newField = coreapi.Field(
                    name=field['name'],
                    required=False, location='query',
                    schema=coreschema.Integer(
                        title=field['name'],
                        description=field['description'] if 'description' in field else None
                    )
                )
            else:
                newField = coreapi.Field(
                    name=field['name'],
                    required=False, location='query',
                    schema=coreschema.String(
                        title=field['name'],
                        description=field['description'] if 'description' in field else None
                    )
                )
            if newField is not None:
                results.append(newField)

        return results

class BusinessFilter(QueryParamBasedFilter):

    def filter_queryset(self, request, queryset, view):
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        btype = request.query_params.get('business_type')

        if latitude is not None or longitude is not None:
            logging.debug("Latitutde & Longitude %s %s " % (latitude, longitude))
            pnt_string = 'POINT(%s %s)' % (longitude, latitude)
            pnt = GEOSGeometry(pnt_string, srid=4326)

            from django.contrib.gis.measure import D
            queryset = queryset.filter(loc__distance_lte=(pnt, D(m=2000))).annotate(
                distance=Distance('loc', pnt)).order_by('distance')
        if btype is not None:
            queryset = queryset.filter(business_type=btype)
        return queryset


class SlotFilter(QueryParamBasedFilter):

    def filter_queryset(self, request, queryset, view):

        date = request.query_params.get('date')
        slot = request.query_params.get('slot')
        if date is None:
            from datetime import date
            date = date.today().strftime("%Y-%m-%d")
            print("Querying for date %s" % date)
        print("Requesting query %s %s" % (date, slot))

        if date is not None:
            queryset = queryset.filter(date=date)
        if slot is not None:
            queryset = queryset.filter(slot=slot)
        queryset = queryset.order_by('date', 'slot')
        return queryset


class ListBusinesses(generics.ListCreateAPIView):
    """
    View to list all users in the system.
    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = []
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    query_params = [{'name': 'latitude', 'type': 'float'}, {'name': 'longitude', 'type': 'float'},
                    {'name': 'business_type', 'type': 'String'}]
    filter_backends = [BusinessFilter]

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """
        return  Business.objects.all()

    def create(self, request, *args, **kwargs):

        try:
            logger.debug("User %s %s", request.user, type(request.user))
            user = get_user_model().objects.get(id=request.user.id)
            if user.profile == 'Consumer':
                return Response("You registered as %s . To add business please contact our customer care center" % request.user.profile,status=status.HTTP_401_UNAUTHORIZED )
            business = Business()
            pnt_string = 'POINT(%s %s)' % (request.data["longitude"], request.data["latitude"])
            business.loc = GEOSGeometry(pnt_string, srid=4326)
            business.business_type = request.data["business_type"].upper()
            business.name = request.data["name"]
            business.slot_size_min = request.data["slot_size_min"]
            business.users_allowed = request.data["users_allowed"]
            business.address = request.data["address"] if "address" in request.data else None
            business.manager = user
            business.save()
            serializer = BusinessSerializer(business)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except:
            import traceback
            traceback.print_exc()
            logger.error("Failed to save business")

        return Response(None, status=status.HTTP_201_CREATED, headers=None)

from rest_framework.schemas import AutoSchema
class ListSlots(generics.ListCreateAPIView):
    """
    View to list all users in the system.
    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = []
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (permissions.IsAuthenticated,)
    queryset = UserSlot.objects.all()
    serializer_class = UserSlotSerializer
    filterset_fields = ['date', 'longitude', 'business_type', "slot"]
    query_params = [{'name': 'slot', 'type': 'string'}, {'name': 'date', 'type': 'string', 'description': 'date in format YYYY-mm-dd'},
                    {'name': 'business_type', 'type': 'String'}]
    filter_backends = [SlotFilter]

    def get_object(self):
        try:

            return Business.objects.get(id=self.kwargs.get('id'))
        except Business.DoesNotExist:
            raise Http404

    def get_queryset(self, id=None):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """

        business = self.get_object()

        return UserSlot.objects.filter(business=business)


    def post(self, request, *args, **kwargs):

        try:
            print(self.request.data)
            user_slot = UserSlot()
            logger.debug("User %s %s", request.user, type(request.user))
            user = get_user_model().objects.get(id=request.user.id)

            business = self.get_object()
            # user_slot.customer_name = self.request.data["customer_name"]
            # user_slot.mobile = self.request.data["mobile"]
            user_slot.slot = request.data['slot']
            user_slot.date = request.data['date']
            if user is not None:
                user_slot.user = user

            if user_slot.date is None or len(user_slot.date) == 0:
                from datetime import date
                user_slot.date = date.today().strftime("%Y-%m-%d")
            user_slot.business = business
            if user_slot.slot not in business.slots:
                return Response("INVALID_SLOT", status=status.HTTP_400_BAD_REQUEST, headers=None)
            print(user_slot.date,user_slot.slot, business)
            slots = UserSlot.objects.filter(business=business, slot=user_slot.slot,date=user_slot.date)
            if len(slots) >= business.users_allowed:
                return Response("ALREADY_FULL", status=status.HTTP_400_BAD_REQUEST, headers=None)
            user_slot.save()
            serializer = UserSlotSerializer(user_slot)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except:
            import traceback
            traceback.print_exc()
            logger.error("Failed to save business")

        return Response(None, status=status.HTTP_201_CREATED, headers=None)

