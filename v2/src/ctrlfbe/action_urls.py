from django.urls import path

from .views import ImageUploadView, IssueApproveView, IssueCloseView, IssueDeleteView

app_name = "actions"

urlpatterns = [
    path("issue-approve/", IssueApproveView.as_view(), name="issue_approve"),
    path("issue-delete/", IssueDeleteView.as_view(), name="issue_delete"),
    path("issue-close/", IssueCloseView.as_view(), name="issue_close"),
    path("images/", ImageUploadView.as_view(), name="upload_images"),
]
