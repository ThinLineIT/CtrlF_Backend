from django.urls import path

from .views import IssueListView

app_name = "issues"

urlpatterns = [
    path("", IssueListView.as_view(), name="issue_list"),
]
