import json

from ctrlf_auth.models import CtrlfUser
from ctrlfbe.models import (
    CtrlfActionType,
    CtrlfContentType,
    CtrlfIssueStatus,
    Issue,
    Note,
    Topic,
)
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from .test_mixin import _get_header, _login


class TestTopicMixin:
    def setUp(self) -> None:
        self.client = Client()
        self.user_data = {"email": "test@test", "password": "12345"}
        self.user = CtrlfUser.objects.create_user(**self.user_data)
        self.note = Note.objects.create(title="test note title")
        self.note.owners.add(self.user)

    def _call_topic_list_api(self, note_id):
        return self.client.get(reverse("notes:topic_list", kwargs={"note_id": note_id}))

    def _call_topic_create_api(self, request_body, token=None):
        return self.client.post(reverse("topics:topic_create"), request_body, **_get_header(token))

    def _call_topic_detail_api(self, topic_id):
        return self.client.get(reverse("topics:topic_detail_update", kwargs={"topic_id": topic_id}))

    def _call_topic_update_api(self, request_body, topic_id, token=None):
        return self.client.put(
            reverse("topics:topic_detail_update", kwargs={"topic_id": topic_id}),
            data=json.dumps(request_body),
            content_type="application/json",
            **_get_header(token),
        )

    def _call_issue_approve_api(self, issue_id, token):
        return self.client.post(reverse("actions:issue_approve"), {"issue_id": issue_id}, **_get_header(token))

    def _make_topics_in_note(self, note, count):
        topic_list = []
        for i in range(count):
            topic_data = {"note": note, "title": f"test topic title {i + 1} to {note.title}"}
            topic = Topic.objects.create(**topic_data)
            topic.owners.add(self.user)
            topic_list.append(topic)
        return topic_list


class TestTopicList(TestTopicMixin, TestCase):
    def _assert_topic_list_and_expected(self, actual, expected):
        for i in range(len(actual)):
            self.assertEqual(actual[i].title, expected[i]["title"])
            self.assertEqual(actual[i].note.id, expected[i]["note"])
            self.assertEqual(actual[i].is_approved, expected[i]["is_approved"])
            self.assertIn(actual[i].owners.first().id, expected[i]["owners"])

    def test_topic_list_should_return_200_ok_and_topic_list(self):
        # Given: Note에 Topic을 10개 생성한다.
        topic_list = self._make_topics_in_note(note=self.note, count=10)
        # And: Note의 id가 주어진다.
        valid_note_id = self.note.id

        # When: Topic List API를 호출한다.
        response = self._call_topic_list_api(valid_note_id)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 응답 데이터의 Topic의 개수는 미리 생성한 Topic의 개수와 같다.
        self.assertEqual(len(response.data), len(topic_list))
        # And: 응답 데이터의 Topic list에 필요한 정보들이 포함되어야한다.
        self._assert_topic_list_and_expected(actual=topic_list, expected=response.data)

    def test_topic_list_should_return_topic_list_only_dependent_on_note_id(self):
        # Given: Note A, B를 생성한다.
        note_a = Note.objects.create(title="note A")
        note_b = Note.objects.create(title="note B")
        # And: Note A에 3개, Note B에 5개의 Topic을 생성한다.
        topic_a_list = self._make_topics_in_note(note=note_a, count=3)
        self._make_topics_in_note(note=note_b, count=5)
        # And: Note A의 id가 주어진다.
        valid_note_id = note_a.id

        # When: Topic List API를 호출한다.
        response = self._call_topic_list_api(valid_note_id)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: Topic 개수는 3개이다.
        self.assertEqual(len(response.data), 3)
        # And: 응답 데이터의 Topic list에 필요한 정보들이 포함되어야한다.
        self._assert_topic_list_and_expected(actual=topic_a_list, expected=response.data)

    def test_topic_list_should_return_200_ok_on_empty_topic_list(self):
        # Given: Note에 Topic을 생성하지 않고, Note의 id만 주어진다.
        valid_note_id = self.note.id

        # When: Topic List API를 호출한다.
        response = self._call_topic_list_api(valid_note_id)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 응답 데이터로 Empty List를 리턴한다.
        self.assertEqual(response.data, [])

    def test_topic_list_should_return_404_not_found_on_invalid_note_id(self):
        # Given: Note에 Topic을 10개 생성한다.
        self._make_topics_in_note(note=self.note, count=10)
        # And: 유효하지 않은 Note id가 주어진다.
        invalid_note_id = 999999

        # When: Topic List API를 호출한다.
        response = self._call_topic_list_api(invalid_note_id)

        # Then: status code는 404를 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And: "노트를 찾을 수 없습니다."라는 메시지를 리턴한다.
        self.assertEqual(response.data["message"], "노트를 찾을 수 없습니다.")


class TestTopicCreate(TestTopicMixin, TestCase):
    def _create_topic_and_issue_by_calling_topic_create_api(self):
        topic_create_request_body = {
            "note_id": self.note.id,
            "title": "test note title",
            "reason": "reason for note create",
        }
        user_token_of_creating_new_topic = _login(self.user_data)
        self._call_topic_create_api(topic_create_request_body, user_token_of_creating_new_topic)

    def _assert_topic_and_expected(self, actual, expected):
        self.assertEqual(actual.title, expected["title"])
        self.assertFalse(actual.is_approved)
        self.assertEqual(actual.note.id, expected["note_id"])
        self.assertIn(self.user, actual.owners.all())

    def _assert_issue_about_topic_create_and_expected(self, actual, expected):
        self.assertEqual(actual.title, expected["title"])
        self.assertEqual(actual.reason, expected["reason"])
        self.assertEqual(actual.owner.id, self.user.id)
        self.assertEqual(actual.status, CtrlfIssueStatus.REQUESTED)
        self.assertEqual(actual.related_model_type, CtrlfContentType.TOPIC)
        self.assertEqual(actual.related_model_id, Topic.objects.first().id)
        self.assertEqual(actual.action, CtrlfActionType.CREATE)
        self.assertEqual(actual.etc, expected["title"])

    def test_topic_create_should_return_201_created_and_create_new_topic_and_new_issue(self):
        # Given: Note id와 Topic title, Issue reason이 주어진다.
        valid_request_body = {
            "note_id": self.note.id,
            "title": "test topic title",
            "reason": "reason for topic create",
        }
        # And: 로그인 해서 토큰을 발급받는다.
        user_token_of_creating_new_topic = _login(self.user_data)

        # When: 인증이 필요한 create topic api를 호출한다.
        response = self._call_topic_create_api(valid_request_body, user_token_of_creating_new_topic)

        # Then: status code는 201을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # And: Topic이 정상적으로 생성된다.
        topic = Topic.objects.first()
        self._assert_topic_and_expected(actual=topic, expected=valid_request_body)
        # And: Issue가 정상적으로 생성된다.
        issue = Issue.objects.first()
        self._assert_issue_about_topic_create_and_expected(actual=issue, expected=valid_request_body)

    def test_topic_create_should_return_404_not_found_on_invalid_note_id(self):
        # Given: 유효하지 않은 Note id가 주어진다.
        invalid_note_id = 8954345
        invalid_request_body = {
            "note_id": invalid_note_id,
            "title": "test topic title",
            "reason": "reason for topic create",
        }
        # And: 로그인 해서 토큰을 발급받는다.
        user_token_of_creating_new_topic = _login(self.user_data)

        # When: 인증이 필요한 Topic Create API를 호출한다.
        response = self._call_topic_create_api(invalid_request_body, user_token_of_creating_new_topic)

        # Then: status code는 404을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And: Topic은 생성되지 않는다.
        self.assertEqual(Topic.objects.count(), 0)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_topic_create_should_return_400_bad_request_on_invalid_title(self):
        # Given: 유효하지 않은 Topic title이 주어진다.
        invalid_topic_title = ""
        invalid_request_body = {
            "note_id": self.note.id,
            "title": invalid_topic_title,
            "reason": "reason for topic create",
        }
        # And: 로그인 해서 토큰을 발급받는다.
        user_token_of_creating_new_topic = _login(self.user_data)

        # When: 인증이 필요한 Topic Create API를 호출한다.
        response = self._call_topic_create_api(invalid_request_body, user_token_of_creating_new_topic)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Topic은 생성되지 않는다.
        self.assertEqual(Topic.objects.count(), 0)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_topic_create_should_return_400_bad_request_on_invalid_reason(self):
        # Given: 유효하지 않은 Issue reason이 주어진다.
        invalid_issue_reason = ""
        invalid_request_body = {
            "note_id": self.note.id,
            "title": "test topic title",
            "reason": invalid_issue_reason,
        }
        # And: 로그인 해서 토큰을 발급받는다.
        user_token_of_creating_new_topic = _login(self.user_data)

        # When: 인증이 필요한 Topic Create API를 호출한다.
        response = self._call_topic_create_api(invalid_request_body, user_token_of_creating_new_topic)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Topic은 생성되지 않는다.
        self.assertEqual(Topic.objects.count(), 0)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_topic_create_should_return_401_unauthorized_on_not_having_token_in_header(self):
        # Given: Note id, Topic title, Issue reason이 주어진다.
        valid_request_body = {
            "note_id": self.note.id,
            "title": "test topic title",
            "reason": "reason for topic create",
        }
        # And: 로그인은 하지 않는다.
        invalid_token = None

        # When: 인증이 필요한 Topic Create API를 호출한다.
        response = self._call_topic_create_api(valid_request_body, invalid_token)

        # Then: status code는 401을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # And: Topic은 생성되지 않는다.
        self.assertEqual(Topic.objects.count(), 0)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_should_change_field_of_is_approved_to_true_on_approving_issue_about_topic_create(self):
        # Given: Topic Create API를 호출하여 미승인 상태의 Topic와 Topic Create Issue를 생성한다.
        self._create_topic_and_issue_by_calling_topic_create_api()
        # And: Topic Create Issue의 id가 주어진다.
        topic_create_issue_id = Issue.objects.first().id
        # And: 해당 Issue에 권한을 가진 token을 발급 받는다.
        user_token_of_having_permission_to_issue_approve = _login(self.user_data)

        # When: Topic Create Issue에 대한 Issue Approve API를 호출한다.
        response = self._call_issue_approve_api(topic_create_issue_id, user_token_of_having_permission_to_issue_approve)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: Topic의 is_approved가 True가 된다.
        topic = Topic.objects.first()
        self.assertTrue(topic.is_approved)

    def test_should_not_change_field_of_is_approved_to_true_on_not_having_permission_to_issue_about_topic_create(self):
        # Given: Topic Create API를 호출하여 미승인 상태의 Topic와 Topic Create Issue를 생성한다.
        self._create_topic_and_issue_by_calling_topic_create_api()
        # And: Topic Create Issue의 id가 주어진다.
        topic_create_issue_id = Issue.objects.first().id
        # And: 해당 Issue에 권한이 없는 token을 발급 받는다.
        another_user_data = {"email": "test2@test.com", "password": "12345"}
        CtrlfUser.objects.create_user(**another_user_data)
        user_token_of_not_having_permission_to_issue_approve = _login(another_user_data)

        # When: Topic Create Issue에 대한 Issue Approve API를 호출한다.
        response = self._call_issue_approve_api(
            topic_create_issue_id, user_token_of_not_having_permission_to_issue_approve
        )

        # Then: status code는 403을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # And: Topic의 is_approved는 그대로 False이다.
        topic = Topic.objects.first()
        self.assertFalse(topic.is_approved)


class TestTopicDetail(TestTopicMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.topic = self._make_topics_in_note(note=self.note, count=1)[0]

    def _assert_topic_detail_and_expected(self, actual, expected):
        self.assertEqual(actual["title"], expected.title)
        self.assertEqual(actual["note"], expected.note.id)
        self.assertEqual(actual["is_approved"], expected.is_approved)
        self.assertIn(expected.owners.first().id, actual["owners"])

    def test_topic_detail_should_return_200_ok_and_topic_detail_data(self):
        # Given: 유효한 Topic id가 주어진다.
        valid_topic_id = self.topic.id

        # When: Topic Detail API를 호출한다.
        response = self._call_topic_detail_api(valid_topic_id)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 응답 데이터에 필요한 정보들을 리턴한다.
        topic = Topic.objects.get(id=valid_topic_id)
        self._assert_topic_detail_and_expected(actual=response.data, expected=topic)

    def test_topic_detail_should_return_404_not_found_on_invalid_topic_id(self):
        # Given: 유효하지 않은 Topic id가 주어진다.
        invalid_topic_id = 1234

        # When: Topic Detail API를 호출한다.
        response = self._call_topic_detail_api(invalid_topic_id)

        # Then: status code는 404를 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And: "토픽을 찾을 수 없습니다."라는 메시지를 리턴한다.
        self.assertEqual(response.data["message"], "토픽을 찾을 수 없습니다.")


class TestTopicUpdate(TestTopicMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.topic = self._make_topics_in_note(note=self.note, count=1)[0]

    def _assert_issue_about_update_topic_and_expected(self, actual, expected):
        self.assertEqual(actual.title, expected["new_title"])
        self.assertEqual(actual.owner, self.user)
        self.assertEqual(actual.reason, expected["reason"])
        self.assertEqual(actual.status, CtrlfIssueStatus.REQUESTED)
        self.assertEqual(actual.related_model_type, CtrlfContentType.TOPIC)
        self.assertEqual(actual.related_model_id, self.topic.id)
        self.assertEqual(actual.action, CtrlfActionType.UPDATE)
        self.assertEqual(actual.etc, self.topic.title)

    def _create_issue_about_topic_update_by_calling_topic_update_api(self):
        topic_update_request_body = {"new_title": "new topic title", "reason": "reason for topic update"}
        user_token_of_creating_update_topic_issue = _login(self.user_data)
        valid_topic_id = self.topic.id
        self._call_topic_update_api(
            topic_update_request_body, valid_topic_id, user_token_of_creating_update_topic_issue
        )

    def test_topic_update_should_return_200_ok_and_create_issue_about_update_topic(self):
        # Given: 새로운 Topic title과 Issue reason이 주어진다.
        valid_request_body = {
            "new_title": "new topic title",
            "reason": "reason for topic update",
        }
        # And: 로그인 해서 토큰을 발급받는다.
        user_token_of_creating_update_topic_issue = _login(self.user_data)
        # And: 수정할 Topic id가 주어진다.
        valid_topic_id = self.topic.id

        # When: 인증이 필요한 Topic Update API를 호출하면,
        response = self._call_topic_update_api(
            valid_request_body, valid_topic_id, user_token_of_creating_update_topic_issue
        )

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 생성된 Issue의 etc값은 Topic의 기존 title, title값은 new_title이다.
        issue = Issue.objects.first()
        self._assert_issue_about_update_topic_and_expected(actual=issue, expected=valid_request_body)

    def test_topic_update_should_return_404_not_found_on_invalid_topic_id(self):
        # Given: 새로운 Topic title과 Issue reason이 주어진다.
        valid_request_body = {
            "new_title": "new topic title",
            "reason": "reason for topic update",
        }
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급는다.
        user_token_of_creating_update_topic_issue = _login(self.user_data)
        # And: 유효하지 않은 Topic id가 주어진다.
        invalid_topic_id = 1122334

        # When: 인증이 필요한 Topic Update API를 호출한다.
        response = self._call_topic_update_api(
            valid_request_body, invalid_topic_id, user_token_of_creating_update_topic_issue
        )

        # Then: status code는 404을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_topic_update_should_return_400_bad_request_on_invalid_new_title(self):
        # Given: 유효하지 않은 새 Topic title이 주어진다.
        invalid_new_title = ""
        invalid_request_body = {
            "new_title": invalid_new_title,
            "reason": "reason for topic update",
        }
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받는다.
        user_token_of_creating_update_topic_issue = _login(self.user_data)
        # And: 수정할 Topic id가 주어진다.
        valid_topic_id = self.topic.id

        # When: 인증이 필요한 Topic Update API를 호출한다.
        response = self._call_topic_update_api(
            invalid_request_body, valid_topic_id, user_token_of_creating_update_topic_issue
        )

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_topic_update_should_return_400_bad_request_on_invalid_reason(self):
        # Given: 유효하지 않은 Issue reason이 주어진다.
        invalid_reason = ""
        invalid_request_body = {
            "new_title": "new topic title",
            "reason": invalid_reason,
        }
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받는다.
        user_token_of_creating_update_topic_issue = _login(self.user_data)
        # And: 수정할 Topic id가 주어진다.
        valid_topic_id = self.topic.id

        # When: 인증이 필요한 Topic Update API를 호출한다.
        response = self._call_topic_update_api(
            invalid_request_body, valid_topic_id, user_token_of_creating_update_topic_issue
        )

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_topic_update_should_return_401_unauthorized_on_not_having_token_in_header(self):
        # Given: 새로운 Topic title과 Issue reason이 주어진다.
        valid_request_body = {
            "new_title": "new topic title",
            "reason": "reason for topic update",
        }
        # And: 수정할 Topic id가 주어진다.
        valid_topic_id = self.topic.id
        # And: 토큰을 발급받지 않는다.
        token = None

        # When: 인증이 필요한 Topic Update API를 호출한다.
        response = self._call_topic_update_api(valid_request_body, valid_topic_id, token)

        # Then: status code는 401을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_should_update_topic_title_on_approving_issue_about_topic_update(self):
        # Given: Topic Update API를 호출하여 Topic Update Issue를 생성한다.
        self._create_issue_about_topic_update_by_calling_topic_update_api()
        # And: Topic Update Issue가 주어진다.
        valid_issue = Issue.objects.first()
        # And: 해당 Issue에 권한이 있는 user token을 발급받는다.
        user_token_of_having_permission_to_issue_approve = _login(self.user_data)

        # When: Topic Update Issue에 대한 Issue Approve API를 호출한다.
        response = self._call_issue_approve_api(valid_issue.id, user_token_of_having_permission_to_issue_approve)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: Topic의 title이 업데이트 된다.
        topic = Topic.objects.get(id=self.topic.id)
        self.assertEqual(topic.title, valid_issue.title)

    def test_should_not_update_topic_title_on_not_having_permission_to_topic_update_issue(self):
        # Given: Topic Update API를 호출하여 Topic Update Issue를 생성한다.
        self._create_issue_about_topic_update_by_calling_topic_update_api()
        # And: Topic Update Issue가 주어진다.
        valid_issue = Issue.objects.first()
        # And: 해당 Issue에 권한이 없는 user token을 발급받는다.
        another_user_data = {"email": "test2@test.com", "password": "12345"}
        CtrlfUser.objects.create_user(**another_user_data)
        user_token_not_having_permission_to_issue = _login(another_user_data)

        # When: Topic Update Issue에 대한 Issue Approve API를 호출한다.
        response = self._call_issue_approve_api(valid_issue.id, user_token_not_having_permission_to_issue)

        # Then: status code는 403을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # And: Topic의 title이 업데이트 되지 않는다.
        topic = Topic.objects.get(id=self.topic.id)
        self.assertNotEqual(topic.title, valid_issue.title)
