from django.urls import path, include

from cs_wiki.views import CategoryListView

urlpatterns = [
    path("mock-category-list", CategoryListView.as_view()),
]
