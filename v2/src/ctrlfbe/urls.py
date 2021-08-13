from ctrlfbe.views import NoteAPIView
from django.urls import path

app_name = "notes"

urlpatterns = [
    path("", NoteAPIView.as_view(), name="retrieve_note_list"),
]
