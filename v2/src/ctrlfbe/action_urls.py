from django.urls import path

from .views import ImageUploadView, IssueApproveView

app_name = "actions"

urlpatterns = [
    path("issue-approve/", IssueApproveView.as_view(), name="issue_approve"),
    path("images/", ImageUploadView.as_view(), name="upload_images")
]
