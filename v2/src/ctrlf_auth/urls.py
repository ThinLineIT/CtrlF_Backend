from ctrlf_auth.views import LoginAPIView
from django.urls import path

app_name = "auth"

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
]
