from django.urls import path

from .views import PageListView

app_name = "topics"

urlpatterns = [
    path("<int:topic_id>/pages", PageListView.as_view(), name="page_list"),
]
