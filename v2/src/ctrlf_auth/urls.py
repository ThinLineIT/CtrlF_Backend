from ctrlf_auth.views import (
    CheckEmailDuplicateView,
    CheckNicknameDuplicateView,
    LoginAPIView,
    SendingAuthEmailView,
    SignUpAPIView,
    TempDeleteEmailView,
)
from django.urls import path
from tests.test_auth import MockAuthAPI

app_name = "auth"

urlpatterns = [
    path("signup/", SignUpAPIView.as_view(), name="signup"),
    path("signup/email", SendingAuthEmailView.as_view(), name="sending_auth_email"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("delete/email", TempDeleteEmailView.as_view(), name="email"),
    path("signup/nickname/duplicate", CheckNicknameDuplicateView.as_view(), name="check_nickname_duplicate"),
    path("signup/email/duplicate", CheckEmailDuplicateView.as_view(), name="check_email_duplicate"),
    path("mock_auth_api ", MockAuthAPI.as_view(), name="mock_auth_api"),
]
