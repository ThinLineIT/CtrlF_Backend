from ctrlf_auth.views import LoginAPIView, SendingAuthEmailView, SignUpAPIView
from django.urls import path

app_name = "auth"

urlpatterns = [
    path("signup/", SignUpAPIView.as_view(), name="signup"),
    path("signup/email", SendingAuthEmailView.as_view(), name="sending_auth_email"),
    path("login/", LoginAPIView.as_view(), name="login"),
]
