from django.urls import path
from . import views


urlpatterns = [
    path("posts/", views.retrieve_post_list, name="retrieve_post_list"),
    path("posts/<int:id>", views.retrieve_post_detail, name="retrieve_post_detail"),
    path("posts/create", views.create_post, name="create_post"),
    path("posts/<int:id>/put/update", views.update_post_with_put, name="update_post_with_put"),
    path("posts/<int:id>/remove", views.remove_post_with_delete, name="remove_post_with_delete"),
]
