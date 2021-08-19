from django.urls import path

from .views import PageListView, TopicDetailUpdateDeleteView

app_name = "topics"

urlpatterns = [
    path("<int:topic_id>/pages", PageListView.as_view(), name="page_list"),
    path("<int:topic_id>", TopicDetailUpdateDeleteView.as_view(), name="topic_detail"),
]
