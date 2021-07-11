from ctrlf_auth.views import LoginAPIView
from django.urls import path

urlpatterns = [
    path("login/", LoginAPIView.as_view()),
]
