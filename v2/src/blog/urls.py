from django.urls import path

from . import views

urlpatterns = [path("posts/<int:post_id>", views.PostDetailUpdateDelete.as_view(), name="post_detail_update_delete")]
