from django.shortcuts import render

# Create your views here.
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, status
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response
from healthybank.settings import COUNTRY_CODE_MAPPING

class CountryDetailsAPI(generics.GenericAPIView):
    throttle_classes = [AnonRateThrottle]

    @method_decorator(cache_page(60 * 60 * 24))
    def get(self,request):

        return Response(data=COUNTRY_CODE_MAPPING, status=status.HTTP_200_OK)
