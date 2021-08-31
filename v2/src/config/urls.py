from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="CTRL-f API Doc",
        default_version="v1",
        description="CTRL-f API Doc",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    authentication_classes=(),
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("admin/", admin.site.urls),
    path("api/auth/", include("ctrlf_auth.urls"), name="auth"),
    path("api/notes/", include("ctrlfbe.note_urls"), name="notes"),
    path("api/topics/", include("ctrlfbe.topic_urls"), name="topics"),
    path("api/issues/", include("ctrlfbe.issue_urls"), name="issues"),
    path("api/pages/", include("ctrlfbe.page_urls"), name="pages"),
]
