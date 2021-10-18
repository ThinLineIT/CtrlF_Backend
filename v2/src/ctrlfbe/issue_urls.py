from django.urls import path

from .views import IssueDetailView, IssueListView

app_name = "issues"

urlpatterns = [
    path("", IssueListView.as_view(), name="issue_list"),
    path("<int:issue_id>", IssueDetailView.as_view(), name="issue_detail"),
]
