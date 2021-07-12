from django.urls import path
from . import views


urlpatterns = [
    path("posts/", views.retrieve_post_list, name="retrieve_post_list"),
    path("posts/<int:id>", views.retrieve_post_detail, name="retrieve_post_detail"),
    # path("posts/create", views.create_post, name="create_post"),
    # path("posts/<int:id>/put/update", views.update_post_with_put, name="update_post_with_put"),
    # path("posts/<int:id>/delete", views.delete_post, name="delete_post")
    path("comments/<int:post_id>", views.retrieve_comment_list, name="retrieve_comment_list"),
]
