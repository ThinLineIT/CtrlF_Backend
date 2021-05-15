from django.urls import path

from cs_wiki.views import IssueListView, NoteListView, PageDetailView

app_name = "cs_wiki"

urlpatterns = [
    path("issues/", IssueListView.as_view(), name="issue-list"),
    path("notes/", NoteListView.as_view(), name="note-list"),
    path("pages/<int:page_id>/", PageDetailView.as_view(), name="page-detail"),
]
