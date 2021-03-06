from django.urls import path

from .views import IssueCount, IssueViewSet

app_name = "issues"

urlpatterns = [
    path("", IssueViewSet.as_view({"get": "list"}), name="issue_list"),
    path(
        "<int:issue_id>/",
        IssueViewSet.as_view(
            {
                "get": "retrieve",
            }
        ),
        name="issue_detail",
    ),
    path("count/", IssueCount.as_view(), name="issue_count"),
]
