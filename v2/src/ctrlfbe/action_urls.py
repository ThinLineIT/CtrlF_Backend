from django.urls import path

from .views import IssueApproveView

app_name = "actions"

urlpatterns = [
    path("issue-approve", IssueApproveView.as_view(), name="issue_approve"),
]
