from ctrlf_auth.models import CtrlfUser
from ctrlfbe.models import CtrlfIssueStatus, Issue
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status


class TestIssueList(TestCase):
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

    def _make_issues(self, count):
        for i in range(1, count + 1):
            Issue.objects.create(
                owner=self.user,
                title=f"test title {i}",
                content=f"test content {1}",
                status=CtrlfIssueStatus.REQUESTED,
            )

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
