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
    path(
        "<int:page_id>/",
        PageViewSet.as_view({"get": "retrieve", "put": "update", "delete": "delete"}),
        name="page_detail_update_delete",
    ),
]
