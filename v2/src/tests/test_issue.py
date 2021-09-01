from ctrlf_auth.models import CtrlfUser
from ctrlfbe.models import (
    ContentRequest,
    CtrlfActionType,
    CtrlfContentStatus,
    CtrlfContentType,
    CtrlfIssueStatus,
    Issue,
    Note,
    Page,
    Topic,
)
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status


class TestIssueList(TestCase):
    def setUp(self):
        self.c = Client()
        self.note_creator1 = CtrlfUser.objects.create_user(email="note_creator1@test.com", password="12345")
        self.note_creator2 = CtrlfUser.objects.create_user(email="note_creator2@test.com", password="12345")
        self.topic_creator = CtrlfUser.objects.create_user(email="topic_creator@test.com", password="12345")
        self.page_creator1 = CtrlfUser.objects.create_user(email="page_creator1@test.com", password="12345")
        self.page_creator2 = CtrlfUser.objects.create_user(email="page_creator2@test.com", password="12345")
        self.note = Note.objects.create(title="test note")
        self.note.owners.add(self.note_creator1)
        self.note.owners.add(self.note_creator2)
        topic_data = {"note": self.note, "title": "test topic"}
        self.topic = Topic.objects.create(**topic_data)
        self.topic.owners.add(self.topic_creator)
        page_data = {"topic": self.topic, "title": "test page"}
        self.page = Page.objects.create(**page_data)
        self.page.owners.add(self.page_creator1)
        self.page.owners.add(self.page_creator2)
        self.owner = CtrlfUser.objects.create_user(email="owner@test.com", password="12345")

    def _add_issues(self, count):
        issue_list = []
        for i in range(0, count):
            content_request_data = {
                "user": self.note_creator1,
                "sub_id": self.note.id,
                "type": CtrlfContentType.NOTE,
                "action": CtrlfActionType.CREATE,
                "status": CtrlfContentStatus.PENDING,
                "reason": "test reason{}".format(i + 1),
                "is_active": True,
            }
            content_request = ContentRequest.objects.create(**content_request_data)
            issue_data = {
                "owner": self.owner,
                "title": "test issue{}".format(i + 1),
                "content": "test content{}".format(i + 1),
                "status": CtrlfIssueStatus.REQUESTED,
                "content_request": content_request,
            }
            issue = Issue.objects.create(**issue_data)
            issue_list.append(issue)
        return issue_list

    def _add_topic_issue(self):
        content_request_data = {
            "user": self.note_creator1,
            "sub_id": self.topic.id,
            "type": CtrlfContentType.TOPIC,
            "action": CtrlfActionType.CREATE,
            "status": CtrlfContentStatus.PENDING,
            "reason": "test reason",
            "is_active": True,
        }
        content_request = ContentRequest.objects.create(**content_request_data)
        issue_data = {
            "owner": self.owner,
            "title": "test issue",
            "content": "test content",
            "status": CtrlfIssueStatus.REQUESTED,
            "content_request": content_request,
        }
        issue = Issue.objects.create(**issue_data)
        return issue

    def _add_page_issue(self):
        content_request_data = {
            "user": self.note_creator1,
            "sub_id": self.page.id,
            "type": CtrlfContentType.PAGE,
            "action": CtrlfActionType.CREATE,
            "status": CtrlfContentStatus.PENDING,
            "reason": "test reason",
            "is_active": True,
        }
        content_request = ContentRequest.objects.create(**content_request_data)
        issue_data = {
            "owner": self.owner,
            "title": "test issue",
            "content": "test content",
            "status": CtrlfIssueStatus.REQUESTED,
            "content_request": content_request,
        }
        issue = Issue.objects.create(**issue_data)
        return issue

    def _call_api(self, cursor, type, mine):
        return self.c.get(reverse("issues:issue_list"), {"cursor": cursor, "type": type, "mine": mine})

    def test_issue_list_should_return_200(self):
        # Given: 2개의 이슈를 생성하고, cursor는 0, type은 [], mine은 false로 주어진다.
        self._add_issues(2)
        given_cursor = 0
        given_type = "[]"
        given_mine = "false"
        # When : API 실행
        response = self._call_api(given_cursor, given_type, given_mine)
        # Then : 상태코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And  : 첫번째 이슈의 title은 "test issue1" 이어야 한다.
        self.assertEqual(response.data["issues"][0]["title"], "test issue1")
        # And  : 두번째 이슈의 title은 "test issue2" 이어야 한다.
        self.assertEqual(response.data["issues"][1]["title"], "test issue2")

    def test_issue_list_shoud_return_200_and_note_owner_is_list(self):
        # Given: 1개의 이슈를 생성하고, cursor는 0, type은 [], mine은 false로 주어진다.
        self._add_issues(1)
        given_cursor = 0
        given_type = "[]"
        given_mine = "false"
        # When : API 실행
        response = self._call_api(given_cursor, given_type, given_mine)
        # Then : 상태코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And  : 이슈의 creator의 노트의 값은 [1, 2] 이어야 한다.
        self.assertEqual(response.data["issues"][0]["creator"]["note"], [1, 2])

    def test_issue_list_shoud_return_200_and_topic_owner_is_list(self):
        # Given: 1개의 콘텐츠 타입이 토픽인 이슈를 생성하고, cursor는 0, type은 [], mine은 false로 주어진다.
        self._add_topic_issue()
        given_cursor = 0
        given_type = "[]"
        given_mine = "false"
        # When : API 실행
        response = self._call_api(given_cursor, given_type, given_mine)
        # Then : 상태코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And  : 이슈의 creator의 노트의 값은 [1, 2] 이어야 한다.
        self.assertEqual(response.data["issues"][0]["creator"]["note"], [1, 2])
        # And  : 이슈의 creator의 토픽의 값은 [1] 이어야 한다.
        self.assertEqual(response.data["issues"][0]["creator"]["topic"], [3])

    def test_issue_list_shoud_return_200_and_page_owner_is_list(self):
        # Given: 1개의 콘텐츠 타입이 페이지인 이슈를 생성하고, cursor는 0, type은 [], mine은 false로 주어진다.
        self._add_page_issue()
        given_cursor = 0
        given_type = "[]"
        given_mine = "false"
        # When : API 실행
        response = self._call_api(given_cursor, given_type, given_mine)
        # Then : 상태코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And  : 이슈의 creator의 노트의 값은 [1, 2] 이어야 한다.
        self.assertEqual(response.data["issues"][0]["creator"]["note"], [1, 2])
        # And  : 이슈의 creator의 토픽의 값은 [1] 이어야 한다.
        self.assertEqual(response.data["issues"][0]["creator"]["topic"], [3])
        # And  : 이슈의 creator의 페이지의 값은 [1, 2] 이어야 한다.
        self.assertEqual(response.data["issues"][0]["creator"]["page"], [4, 5])

    def test_issue_list_should_return_200_by_thirty_issue_list(self):

        # Given: 30개의 이슈를 생성하고, cursor는 0, type은 [], mine은 false로 주어진다.
        self._add_issues(30)
        given_cursor = 0
        given_type = "[]"
        given_mine = "false"
        # When : API 실행
        response = self._call_api(given_cursor, given_type, given_mine)
        # Then : 상태코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And  : next_cursor는 30을 리턴한다.
        self.assertEqual(response.data["next_cursor"], 30)
        # And  : 시작 cursor부터 30개의 이슈 리스트를 return 해야함.
        self.assertEqual(len(response.data["issues"]), 30)

    def test_issue_list_should_return_200_by_ten_issue_list(self):
        # Given: 10개의 이슈를 생성하고, cursor는 0, type은 [], mine은 false로 주어진다.
        self._add_issues(10)
        given_cursor = 5
        given_type = "[]"
        given_mine = "false"
        # When : API 실행
        response = self._call_api(given_cursor, given_type, given_mine)
        # Then : 상태코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And  : next_cursor는 10을 리턴한다.
        self.assertEqual(response.data["next_cursor"], 10)
        # And  : 시작 cursor부터 5개의 이슈 리스트를 return 해야함.
        self.assertEqual(len(response.data["issues"]), 5)

    def test_issue_list_should_return_200_by_ten_issue_list_and_cursor_fifteen(self):
        # Given: 10개의 이슈를 생성하고, cursor는 15로 주어진다.
        self._add_issues(10)
        given_cursor = 15
        given_type = "[]"
        given_mine = "false"
        # When : API 실행
        response = self._call_api(given_cursor, given_type, given_mine)
        # Then : 상태코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And  : next_cursor는 10을 리턴한다.
        self.assertEqual(response.data["next_cursor"], 10)
        # And  : 빈 배열을 return 해야함.
        self.assertEqual(response.data["issues"], [])

    def test_issue_list_should_return_200_by_empty_issue_list(self):
        # Given: 이슈 생성 없이, cursor는 0, type은 [], mine은 false로 주어진다.
        given_cursor = 0
        given_type = "[]"
        given_mine = "false"
        # When : API 실행
        response = self._call_api(given_cursor, given_type, given_mine)
        # Then : 상태코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And  : next_cursor는 0, type은 [], mine은 false 리턴한다.
        self.assertEqual(response.data["next_cursor"], 0)
        # And  : 빈 배열을 return 해야함.
        self.assertEqual(response.data["issues"], [])
