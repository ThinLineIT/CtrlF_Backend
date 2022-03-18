from django.urls import path

from .views import (
    ImageUploadView,
    IssueApproveView,
    IssueCloseView,
    IssueDeleteView,
    IssueRejectView,
    IssueUpdatePermissionCheck,
    IssueUpdateView,
)

app_name = "actions"

urlpatterns = [
    path("issue-approve/", IssueApproveView.as_view(), name="issue_approve"),
    path("issue-delete/", IssueDeleteView.as_view(), name="issue_delete"),
    path("issue-close/", IssueCloseView.as_view(), name="issue_close"),
    path("issue-update/", IssueUpdateView.as_view(), name="issue_update"),
    path("issue-reject/", IssueRejectView.as_view(), name="issue_reject"),
    path("issue-update-permission-check/", IssueUpdatePermissionCheck.as_view(), name="issue_update_permission_check"),
    path("images/", ImageUploadView.as_view(), name="upload_images"),
]
