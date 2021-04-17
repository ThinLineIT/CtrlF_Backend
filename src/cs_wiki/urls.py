from django.urls import path, include

from cs_wiki.views import CategoryListView, NoteListView, AllPageCountView

urlpatterns = [
    path("mock-category-list", CategoryListView.as_view()),
    path("notes/", NoteListView.as_view()),
    path("all_page_count/", AllPageCountView.as_view()),
]
