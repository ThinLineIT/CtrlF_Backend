from django.urls import path

from .views import NoteAPIView, NoteDetailUpdateDeleteView, TopicListView

app_name = "notes"

urlpatterns = [
    path("", NoteAPIView.as_view(), name="retrieve_note_list"),
    path("<int:note_id>", NoteDetailUpdateDeleteView.as_view(), name="note_detail_update_delete"),
    path("<int:note_id>/topics", TopicListView.as_view(), name="topic_list"),
]
