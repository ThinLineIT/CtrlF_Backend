from django.urls import path

from .views import NoteDetailUpdateDeleteView, NoteListCreateView, TopicListView

app_name = "notes"

urlpatterns = [
    path("", NoteListCreateView.as_view(), name="note_list_create"),
    path("<int:note_id>", NoteDetailUpdateDeleteView.as_view(), name="note_detail_update_delete"),
    path("<int:note_id>/topics", TopicListView.as_view(), name="topic_list"),
]
