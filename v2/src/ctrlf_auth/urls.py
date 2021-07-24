from ctrlf_auth.views import LoginAPIView, SignUpAPIView
from django.urls import path

app_name = "auth"

urlpatterns = [
    path("signup/", SignUpAPIView.as_view(), name="signup"),
    path("login/", LoginAPIView.as_view(), name="login"),
]
