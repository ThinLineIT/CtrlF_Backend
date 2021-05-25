from django.urls import path

from cs_wiki.views import (
    HomeView,
    IssueListView,
    IssueDetailView,
    NoteListView,
    NoteDetailView,
    TopicView,
    TopicDetailView,
    PageView,
    PageDetailView,
    PagesCountView,
)

app_name = "cs_wiki"

urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
    path("pages-count/", PagesCountView.as_view(), name="pages-count"),
    path("issues/", IssueListView.as_view(), name="issue-list"),
    path("issues/<int:issue_id>/", IssueDetailView.as_view(), name="issue-detail"),
    path("notes/", NoteListView.as_view(), name="note-list"),
    path("notes/<int:note_id>/", NoteDetailView.as_view(), name="note-detail"),
    path("topics/", TopicView.as_view(), name="topic"),
    path("topics/<int:topic_id>/", TopicDetailView.as_view(), name="topic-detail"),
    path("pages/", PageView.as_view(), name="page"),
    path("pages/<int:page_id>/", PageDetailView.as_view(), name="page-detail"),
]
