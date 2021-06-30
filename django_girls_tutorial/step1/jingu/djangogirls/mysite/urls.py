from django.conf.urls import include, url
from django.contrib import admin

from django.contrib.auth import views

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^accounts/login/$", views.login, name="login"),
    url(r"^accounts/logout/$", views.logout, name="logout", kwargs={"next_page": "/"}),
    url(r"", include("blog.urls")),
    url(
        r"^post/(?P<pk>\d+)/comment/$",
        views.add_comment_to_post,
        name="add_comment_to_post",
    ),
]
