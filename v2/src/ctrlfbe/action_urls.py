from django.urls import path

from .views import ImageUploadView, IssueApproveView, IssueDeleteView

app_name = "actions"

urlpatterns = [
    path("issue-approve/", IssueApproveView.as_view(), name="issue_approve"),
    path("issue-delete/", IssueDeleteView.as_view(), name="issue_delete"),
    path("images/", ImageUploadView.as_view(), name="upload_images"),
]
