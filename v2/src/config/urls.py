"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import path
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response

schema_view = get_schema_view(
    openapi.Info(
        title="Ctrl-f BE",
        default_version="v1",
        description="Ctrl-f BE API Doc",
        terms_of_service="",
        contact=openapi.Contact(name="test", email="test@test.com"),
        license=openapi.License(name="Ctrl-f BE License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


@swagger_auto_schema(method="get")
@api_view(["GET"])
def helloworld(request):
    return Response({"hello": "world"})


urlpatterns = [path("admin/", admin.site.urls)]

if settings.DEBUG:
    urlpatterns += [
        path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
        path("helloworld", helloworld),
    ]
