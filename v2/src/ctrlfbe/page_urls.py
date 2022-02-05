from django.urls import path

from .views import PageViewSet

app_name = "pages"

urlpatterns = [
    path(
        "",
        PageViewSet.as_view(
            {
                "post": "create",
            }
        ),
        name="page_create",
    ),
    path("<int:page_id>/", PageViewSet.as_view({"put": "update"}), name="page_update"),
    path("<int:page_id>/<int:version_no>/", PageViewSet.as_view({"get": "retrieve"}), name="page_detail"),
]
