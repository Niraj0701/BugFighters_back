# Create your views here.

from rest_framework import serializers
from business.models import Business
from django.contrib.gis.geos import GEOSGeometry

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework import authentication, permissions
import logging
from django.http import HttpResponse

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
            print(obj.loc.x)
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

    filterset_fields = ['latitude','longitude','btype']

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """
        print(self.kwargs, )
        lat = self.request.query_params.get('latitude')
        longt = self.request.query_params.get('longitude')
        logging.debug("Latitutde & Longitude %s %s " % ( lat, longt))
        pnt_string = 'POINT(%s %s)' % ( lat, longt)
        pnt = GEOSGeometry(pnt_string, srid=4326)
        return Business.objects.filter(loc__distance_gte=(pnt,500))


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
