from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView
from rest_framework.serializers import Serializer
from rest_framework.throttling import AnonRateThrottle
from items.models import Item

class ItemSerializer(Serializer):
    class Meta:
        model = Item

class ItemView(ListAPIView):
    throttle_classes = [AnonRateThrottle]

    def get_queryset(self):
        return
