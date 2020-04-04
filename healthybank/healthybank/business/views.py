# Create your views here.

from rest_framework import serializers
from business.models import Business
from django.contrib.gis.geos import GEOSGeometry

from rest_framework import generics, status
from rest_framework.response import Response
import logging
logger = logging.getLogger(__name__)

class BusinessSerializer(serializers.ModelSerializer):
    coords = serializers.SerializerMethodField('get_coords',read_only=False)
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    class Meta:
        model = Business
        fields = ['name', 'coords', 'id',"business_type",'users_allowed','slot_size_min',"longitude","latitude" ]
        # exclude = ['organization']
        # fields = '__all__'

    def get_coords(self, obj):
        if isinstance(obj, Business):
            return { "latitude": obj.loc.x, "longitude":obj.loc.y}
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
    serializer_class =  BusinessSerializer
    filterset_fields = ['latitude','longitude', 'business_type']

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """
        latitude = self.request.query_params.get('latitude')
        longitude = self.request.query_params.get('longitude')
        if latitude is not None or longitude is not None:
            logging.debug("Latitutde & Longitude %s %s " % (latitude, longitude))
            pnt_string = 'POINT(%s %s)' % (latitude, longitude)
            pnt = GEOSGeometry(pnt_string, srid=4326)
            return Business.objects.filter(loc__distance_gte=(pnt,500))
        return Business.objects.all()

    def create(self, request, *args, **kwargs):

        try:
            business=Business()
            pnt_string = 'POINT(%s %s)' % (request.data["latitude"], request.data["longitude"])
            business.loc  = GEOSGeometry(pnt_string, srid=4326)
            business.business_type =  request.data["business_type"]
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
