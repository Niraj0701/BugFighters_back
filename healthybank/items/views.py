from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView
from rest_framework.serializers import Serializer
from rest_framework.throttling import AnonRateThrottle
from items.models import Item
from rest_framework import filters
from commons.utils import StandardResultsSetPagination
class ItemSerializer(Serializer):
    class Meta:
        model = Item

class ItemView(ListAPIView):
    throttle_classes = [AnonRateThrottle]
    serializer_class = ItemSerializer
    filter_backends = [filters.SearchFilter]
    search_fields=['name']
    pagination_class = StandardResultsSetPagination

    queryset = Item.objects.all()