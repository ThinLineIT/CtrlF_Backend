from django.urls import path

from .views import PostRetrieveListView

urlpatterns = [
    path("", PostRetrieveListView.as_view(), name="retrieve_post_list"),
]
