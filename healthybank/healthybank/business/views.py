# Create your views here.
from django.http import Http404
from rest_framework import serializers
from business.models import Business, UserSlot
from django.contrib.gis.geos import GEOSGeometry

from rest_framework import generics, status
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


class BusinessSerializer(serializers.ModelSerializer):
    coords = serializers.SerializerMethodField('get_coords', read_only=False)
    # slots = serializers.SerializerMethodField('get_slots', read_only=True)
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    distance = serializers.SerializerMethodField('get_distance',read_only=True)

    class Meta:
        model = Business
        fields = ['name', 'coords', 'id', "business_type", 'users_allowed', 'slot_size_min', "longitude", "latitude",
                  "slots", "start_time", "end_time","distance"]
        # exclude = ['organization']
        # fields = '__all__'

    def get_coords(self, obj):
        if isinstance(obj, Business):
            return {"latitude": obj.loc.x, "longitude": obj.loc.y}
        return {}

    def get_distance(self,obj):

        latitude = self.context['request'].query_params.get('latitude')
        longitude = self.context['request'].query_params.get('longitude')
        if latitude is not None and longitude is not None:
            request_location = GEOSGeometry('SRID=4326;POINT(%s %s)' % ( latitude, longitude))

            return obj.loc.distance(request_location) * 100 * 1000
        return 0



class UserSlotSerializer(serializers.ModelSerializer):
    business = serializers.SerializerMethodField('get_business', read_only=True)
    date = serializers.DateField(required=False)
    class Meta:
        model = UserSlot
        fields = '__all__'

    def get_business(self, obj):
        if isinstance(obj, UserSlot):
            return {"name": obj.business.name, "id": obj.business.id, "type": obj.business.business_type}
        return {}


class ListBusinesses(generics.ListCreateAPIView):
    """
    View to list all users in the system.
    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = []
    # permission_classes = [permissions.IsAdminUser]
    # permission_classes = (permissions.IsAuthenticated,)
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    filterset_fields = ['latitude', 'longitude', 'business_type']

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """
        latitude = self.request.query_params.get('latitude')
        longitude = self.request.query_params.get('longitude')
        btype = self.request.query_params.get('business_type')
        business_query = Business.objects.all()
        if latitude is not None or longitude is not None:
            logging.debug("Latitutde & Longitude %s %s " % (latitude, longitude))
            pnt_string = 'POINT(%s %s)' % (latitude, longitude)
            pnt = GEOSGeometry(pnt_string, srid=4326)
            business_query = business_query.filter(loc__distance_gte=(pnt, 500))
        if btype is not None:
            business_query = business_query.filter(business_type=btype)

        return business_query

    def create(self, request, *args, **kwargs):

        try:
            business = Business()
            pnt_string = 'POINT(%s %s)' % (request.data["latitude"], request.data["longitude"])
            business.loc = GEOSGeometry(pnt_string, srid=4326)
            business.business_type = request.data["business_type"]
            business.name = request.data["name"]
            business.slot_size_min = request.data["slot_size_min"]
            business.users_allowed = request.data["users_allowed"]
            business.save()
            serializer = BusinessSerializer(business)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except:
            import traceback
            traceback.print_exc()
            logger.error("Failed to save business")

        return Response(None, status=status.HTTP_201_CREATED, headers=None)


class ListSlots(generics.ListCreateAPIView):
    """
    View to list all users in the system.
    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = []
    # permission_classes = [permissions.IsAdminUser]
    # permission_classes = (permissions.IsAuthenticated,)
    queryset = UserSlot.objects.all()
    serializer_class = UserSlotSerializer
    filterset_fields = ['date', 'longitude', 'business_type', "slot"]

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

        date = self.request.query_params.get('date')
        slot = self.request.query_params.get('slot')
        if date is None:
            from datetime import date
            date = date.today().strftime("%Y-%m-%d")
            print("Querying for date %s" % date)
        business = self.get_object()
        print("Requesting query %s %s" % (date, business))

        user_slot_query = UserSlot.objects.filter(business=business)
        if date is not None:
            user_slot_query = user_slot_query.filter(date=date)
        if slot is not None:
            user_slot_query = user_slot_query.filter(slot=slot)
        return user_slot_query

    def post(self, request, *args, **kwargs):

        try:
            user_slot = UserSlot()

            business = self.get_object()
            user_slot.customer_name = self.request.data["customer_name"]
            user_slot.mobile = self.request.data["mobile"]
            user_slot.slot = self.request.data["slot"]
            user_slot.date = self.request.data["date"]

            if user_slot.date is None or len(user_slot.date) == 0:
                from datetime import date
                user_slot.date = date.today().strftime("%Y-%m-%d")
            print("DATE", user_slot.date)
            user_slot.business = business
            if user_slot.slot not in business.slots:
                return Response("INVALID_SLOT", status=status.HTTP_400_BAD_REQUEST, headers=None)
            slots = UserSlot.objects.filter(business=business, slot=self.request.data["slot"],date=user_slot.date)
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

#
# class ListSlots(generics.ListCreateAPIView):
#     """
#     View to list all users in the system.
#     * Requires token authentication.
#     * Only admin users are able to access this view.
#     """
#     # authentication_classes = []
#     # permission_classes = [permissions.IsAdminUser]
#     # permission_classes = (permissions.IsAuthenticated,)
#     queryset = UserSlot.objects.all()
#     serializer_class = UserSlotSerializer
#     filterset_fields = ['date', 'longitude', 'business_type', "slot"]
#
#     def get_object(self):
#         try:
#
#             return User.objects.get(id=self.kwargs.get('id'))
#         except Business.DoesNotExist:
#             raise Http404
#
#     def get_queryset(self, id=None):
#         """
#         This view should return a list of all the purchases for
#         the user as determined by the username portion of the URL.
#         """
#
#         date = self.request.query_params.get('date')
#         slot = self.request.query_params.get('slot')
#         if date is None:
#             from datetime import date
#             date = date.today().strftime("%Y-%m-%d")
#             print("Querying for date %s" % date)
#         business = self.get_object()
#         print("Requesting query %s %s" % (date, business))
#
#         user_slot_query = UserSlot.objects.filter(business=business)
#         if date is not None:
#             user_slot_query = user_slot_query.filter(date=date)
#         if slot is not None:
#             user_slot_query = user_slot_query.filter(slot=slot)
#         return user_slot_query
#
#     def post(self, request, *args, **kwargs):
#
#         try:
#             user_slot = UserSlot()
#
#             business = self.get_object()
#             user_slot.customer_name = self.request.data["customer_name"]
#             user_slot.mobile = self.request.data["mobile"]
#             user_slot.slot = self.request.data["slot"]
#             user_slot.date = self.request.data["date"]
#
#             if user_slot.date is None or len(user_slot.date) == 0:
#                 from datetime import date
#                 user_slot.date = date.today().strftime("%Y-%m-%d")
#             print("DATE", user_slot.date)
#             user_slot.business = business
#             if user_slot.slot not in business.slots:
#                 return Response("INVALID_SLOT", status=status.HTTP_400_BAD_REQUEST, headers=None)
#             slots = UserSlot.objects.filter(business=business, slot=self.request.data["slot"],date=user_slot.date)
#             if len(slots) >= business.users_allowed:
#                 return Response("ALREADY_FULL", status=status.HTTP_400_BAD_REQUEST, headers=None)
#             user_slot.save()
#             serializer = UserSlotSerializer(user_slot)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         except:
#             import traceback
#             traceback.print_exc()
#             logger.error("Failed to save business")
#
#         return Response(None, status=status.HTTP_201_CREATED, headers=None)
