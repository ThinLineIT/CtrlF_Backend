from django.urls import path

from .views import PageViewSet, TopicViewSet

app_name = "topics"

urlpatterns = [
    path(
        "",
        TopicViewSet.as_view(
            {
                "post": "create",
            }
        ),
        name="topic_create",
    ),
    path(
        "<int:topic_id>/pages/",
        PageViewSet.as_view(
            {
                "get": "list",
            }
        ),
        name="page_list",
    ),
    path(
        "<int:topic_id>/",
        TopicViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "delete",
            }
        ),
        name="topic_detail_update_delete",
    ),
]
