from django.urls import path

from .views import NoteViewSet, TopicViewSet

app_name = "notes"

urlpatterns = [
    path(
        "",
        NoteViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="note_list_create",
    ),
    path(
        "<int:note_id>/topics/",
        TopicViewSet.as_view(
            {
                "get": "list",
            }
        ),
        name="topic_list",
    ),
    path("<int:note_id>/", NoteViewSet.as_view({"get": "retrieve"}), name="note_detail_update_delete"),
]
