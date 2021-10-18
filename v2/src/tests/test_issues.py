from ctrlf_auth.models import CtrlfUser
from ctrlfbe.models import CtrlfIssueStatus, Issue
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status


class IssueListTextMixin:
    def setUp(self) -> None:
        self.client = Client()
        self.user_data = {
            "email": "test@test.com",
            "password": "12345",
        }
        self.user = CtrlfUser.objects.create_user(**self.user_data)

    def _call_api(self, cursor):
        return self.client.get(
            reverse("issues:issue_list"),
            {"cursor": cursor},
        )

    def _call_detail_api(self, issue_id):
        return self.client.get(reverse("issues:issue_detail", kwargs={"issue_id": issue_id}))

    def _make_issues(self, count):
        for i in range(1, count + 1):
            Issue.objects.create(
                owner=self.user,
                title=f"test title {i}",
                content=f"test content {1}",
                status=CtrlfIssueStatus.REQUESTED,
            )


class TestIssueList(IssueListTextMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_issue_list_should_return_200(self):
        # Given: 미리 30개의 이슈를 생성하고, 시작 cursor가 주어진다.
        self._make_issues(30)
        given_cursor = 0

        # When: issue list api를 호출한다.
        response = self._call_api(given_cursor)

        # Then: status code 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: next_cursor는 30을 리턴한다.
        self.assertEqual(response.data["next_cursor"], 30)
        # And: 시작 cursor부터 30개의 issue list를 리턴한다.
        self.assertEqual(len(response.data["issues"]), 30)

    def test_issue_list_on_issue_count_less_than_30(self):
        # Given: 10개의 이슈를 생성하고 시작 cursor를 3으로 주어진다.
        self._make_issues(10)
        given_cursor = 3

        # When: issue list api를 호출한다.
        response = self._call_api(given_cursor)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: next_cursor는 10을 리턴한다.
        self.assertEqual(response.data["next_cursor"], 10)
        # And: 시작 cursor부터 7개의 issue list를 리턴한다.
        self.assertEqual(len(response.data["issues"]), 7)

    def test_issue_list_on_empty_issue(self):
        # Given: 이슈 생성 없이, cursor만 주어진다.
        given_cursor = 0

        # When: issue list api를 호풀한다.
        response = self._call_api(given_cursor)

        # Then: status code는 200을 리턴한다
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: next_cursor는 0을 리턴한다.
        self.assertEqual(response.data["next_cursor"], 0)
        # And: empty list를 리턴한다.
        self.assertEqual(len(response.data["issues"]), 0)


class TestIssueDetail(IssueListTextMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_issue_detail_should_return_issue_on_success(self):
        # Given: 이슈를 1개 생성 하였을 때,
        issue = Issue.objects.create(
            owner=self.user,
            title="test title",
            content="test content",
            status=CtrlfIssueStatus.REQUESTED,
        )

        # When: issue list api를 호출한다.
        response = self._call_detail_api(issue_id=issue.id)

        # Then: status code는 200을 리턴한다
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 생성된 이슈와 값이 일치해야한다
        self.assertEqual(response.data["title"], "test title")
        self.assertEqual(response.data["content"], "test content")
        self.assertEqual(response.data["status"], CtrlfIssueStatus.REQUESTED)
        self.assertEqual(response.data["owner"], self.user.email)

    def test_issue_detail_should_return_404_not_found_on_issue_does_not_exist(self):
        # Given: 이슈를 생성하지 않았을 때,
        invalid_issue_id = 1122334

        # When: issue list api를 호출한다.
        response = self._call_detail_api(issue_id=invalid_issue_id)

        # Then: status code는 404을 리턴한다
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
