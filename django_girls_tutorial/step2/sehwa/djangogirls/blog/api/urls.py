from django.urls import path
from . import views


urlpatterns = [
    path("posts/", views.retrieve_post_list, name="retrieve_post_list"),
    path("posts/<int:id>", views.retrieve_post_detail, name="retrieve_post_detail"),
]
