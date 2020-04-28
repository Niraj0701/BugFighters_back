"""healthybank URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include
from business.views import ListBusinesses, ListSlots
from users.views import UsersAPI, UserSelfProfileAPI,UserSlots,UserVerificationAPI
from commons.views import CountryDetailsAPI
from otp.views import RequestOTP,OpenRequestOTP
from django.conf import settings
from django.http import HttpResponse
from users.views import MobileAuthenticationView, UnAuthenticatedPasswordUpdateWithOTPAPI, AuthenticatedPasswordUpdateWithOTPAPI

def health_check(request):
    return HttpResponse("Success")


from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0),
      name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    url(r'^health', health_check, name="health_check"),
    url(r'^api/businesses', ListBusinesses.as_view()),
    url(r'^api/business/(?P<id>\w{0,50})/slots', ListSlots.as_view()),
    url(r'^api/user/(?P<id>\w{0,50})/slots', UserSlots.as_view()),
    url(r'^api/user/(?P<id>\w{0,50})/verify', UserVerificationAPI.as_view()),
    url(r'^api/users/', UsersAPI.as_view()),
    url(r'^api/otp/', RequestOTP.as_view()),
    url(r'^api/ootp/', OpenRequestOTP.as_view()),
    url(r'^api/password/', UnAuthenticatedPasswordUpdateWithOTPAPI.as_view()),
    url(r'^api/password/secure', AuthenticatedPasswordUpdateWithOTPAPI.as_view()),
    url(r'^api/me/', UserSelfProfileAPI.as_view()),
    path('api/signin/', MobileAuthenticationView.as_view()),
    url(r'^api/countries/', CountryDetailsAPI.as_view()),
    url(r'api-docs/', include('rest_framework.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
