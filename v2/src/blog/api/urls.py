from django.urls import path

from .views import PostRetrieveDetailView, PostRetrieveListView

urlpatterns = [
    path("", PostRetrieveListView.as_view(), name="retrieve_post_list"),
    path("<int:id>", PostRetrieveDetailView.as_view(), name="retrieve_post_detail"),
]
