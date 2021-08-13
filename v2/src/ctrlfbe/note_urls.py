from django.urls import path

from .views import NoteDetailUpdateDeleteView

app_name = "notes"

urlpatterns = [
    path("<int:note_id>", NoteDetailUpdateDeleteView.as_view(), name="note_detail_update_delete"),
]