import json

from ctrlf_auth.models import CtrlfUser
from ctrlfbe.models import (
    CtrlfActionType,
    CtrlfContentType,
    CtrlfIssueStatus,
    Issue,
    Note,
)
from ctrlfbe.serializers import IssueCreateSerializer
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from .test_mixin import _get_header, _login


class NoteTestMixin:
    def setUp(self) -> None:
        self.client = Client()
        self.user_data = {"email": "test@test.com", "password": "12345"}
        self.user = CtrlfUser.objects.create_user(**self.user_data)

    def _call_note_list_api(self, cursor):
        return self.client.get(reverse("notes:note_list_create"), {"cursor": cursor})

    def _call_note_create_api(self, request_body, token=None):
        return self.client.post(reverse("notes:note_list_create"), request_body, **_get_header(token))

    def _call_note_detail_api(self, note_id):
        return self.client.get(reverse("notes:note_detail_update_delete", kwargs={"note_id": note_id}))

    def _call_note_update_api(self, request_body, note_id, token=None):
        return self.client.put(
            reverse("notes:note_detail_update_delete", kwargs={"note_id": note_id}),
            data=json.dumps(request_body),
            content_type="application/json",
            **_get_header(token),
        )

    def _call_note_delete_api(self, request_body, note_id, token=None):
        return self.client.delete(
            reverse("notes:note_detail_update_delete", kwargs={"note_id": note_id}),
            data=json.dumps(request_body),
            content_type="application/json",
            **_get_header(token),
        )

    def _call_issue_approve_api(self, issue_id, token):
        return self.client.post(reverse("actions:issue_approve"), {"issue_id": issue_id}, **_get_header(token))

    def _make_note_list(self, count):
        note_list = []
        for i in range(count):
            note = Note.objects.create(title=f"test title {i + 1}")
            note.owners.add(self.user)
            note_list.append(note)
        return note_list


class TestNoteList(NoteTestMixin, TestCase):
    def _assert_note_list_and_expected(self, actual, expected):
        for i in range(len(actual)):
            self.assertEqual(actual[i]["title"], expected[i].title)
            self.assertEqual(actual[i]["id"], expected[i].id)
            self.assertEqual(actual[i]["is_approved"], expected[i].is_approved)
            self.assertIn(expected[i].owners.first().id, actual[i]["owners"])

    def test_note_list_should_return_200_ok_and_next_cursor_and_note_list(self):
        # Given: Note를 30개 생성한다.
        note_list = self._make_note_list(30)
        # And: 시작 cursor가 주어진다.
        start_cursor = 0

        # When: Note List API를 호출한다.
        response = self._call_note_list_api(start_cursor)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: next_cursor는 30을 리턴한다.
        self.assertEqual(response.data["next_cursor"], 30)
        # And: start_cursor부터 30개의 Note list를 리턴한다.
        self.assertEqual(len(response.data["notes"]), 30)
        # And: 응답 데이터로 필요한 정보들을 리턴한다.
        self._assert_note_list_and_expected(
            actual=response.data["notes"], expected=note_list[start_cursor : start_cursor + 30]
        )

    def test_note_list_should_return_note_list_max_length_30(self):
        # Given: Note를 50개 생성한다.
        note_list = self._make_note_list(50)
        # And: 시작 cursor가 주어진다.
        start_cursor = 11

        # When: Note List API를 호출한다.
        response = self._call_note_list_api(start_cursor)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: next_cursor는 41을 리턴한다.
        self.assertEqual(response.data["next_cursor"], 41)
        # And: start_cursor부터 30개의 Note list를 리턴한다.
        self.assertEqual(len(response.data["notes"]), 30)
        # And: 응답 데이터로 필요한 정보들을 리턴한다.
        self._assert_note_list_and_expected(
            actual=response.data["notes"], expected=note_list[start_cursor : start_cursor + 30]
        )

    def test_note_list_should_return_200_ok_on_note_count_less_than_30(self):
        # Given: Note를 10개 생선한다.
        note_list = self._make_note_list(10)
        # And: 시작 cursor가 주어진다.
        start_cursor = 3

        # When: Note List API를 호출한다.
        response = self._call_note_list_api(start_cursor)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: next_cursor는 10을 리턴한다.
        self.assertEqual(response.data["next_cursor"], 10)
        # And: 시작 cursor부터 7개의 note list를 리턴한다.
        self.assertEqual(len(response.data["notes"]), 7)
        # And: 응답 데이터로 필요한 정보들을 리턴한다.
        self._assert_note_list_and_expected(
            actual=response.data["notes"], expected=note_list[start_cursor : start_cursor + 30]
        )

    def test_note_list_should_return_200_ok_and_empty_list_on_not_exist_note(self):
        # Given: 노트 생성 없이, cursor만 주어진다.
        start_cursor = 0

        # When: Note List API를 호출한다.
        response = self._call_note_list_api(start_cursor)

        # Then: status code는 200을 리턴한다
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: next_cursor는 0을 리턴한다.
        self.assertEqual(response.data["next_cursor"], 0)
        # And: empty list를 리턴한다.
        self.assertEqual(response.data["notes"], [])


class TestNoteCreate(NoteTestMixin, TestCase):
    def _create_note_and_issue_by_calling_note_create_api(self):
        note_create_request_body = {"title": "test note title", "reason": "reason for note create"}
        user_token_of_creating_new_note = _login(self.user_data)
        self._call_note_create_api(note_create_request_body, user_token_of_creating_new_note)

    def _assert_note_and_expected(self, actual, expected):
        self.assertEqual(actual.title, expected["title"])
        self.assertFalse(actual.is_approved)
        self.assertIn(self.user, actual.owners.all())

    def _assert_issue_about_note_create_and_expected(self, actual, expected):
        self.assertEqual(actual.title, expected["title"])
        self.assertEqual(actual.reason, expected["reason"])
        self.assertEqual(actual.owner.id, self.user.id)
        self.assertEqual(actual.status, CtrlfIssueStatus.REQUESTED)
        self.assertEqual(actual.related_model_type, CtrlfContentType.NOTE)
        self.assertEqual(actual.related_model_id, Note.objects.first().id)
        self.assertEqual(actual.action, CtrlfActionType.CREATE)
        self.assertEqual(actual.etc, expected["title"])

    def test_note_create_should_return_201_created_and_create_new_note_and_new_issue(self):
        # Given: Note title과 Issue reason이 주어진다.
        valid_request_body = {"title": "test note title", "reason": "reason for note create"}
        # And: 로그인을 해서 토큰을 발급받는다.
        user_token_of_creating_new_note = _login(self.user_data)

        # When: 인증이 필요한 Note Create API를 호출한다.
        response = self._call_note_create_api(valid_request_body, user_token_of_creating_new_note)

        # Then: status code는 201을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # And: Note가 정상적으로 생성된다.
        note = Note.objects.first()
        self._assert_note_and_expected(actual=note, expected=valid_request_body)
        # And: Issue가 정상적으로 생성된다.
        issue = Issue.objects.first()
        self._assert_issue_about_note_create_and_expected(actual=issue, expected=valid_request_body)

    def test_create_note_should_return_400_bad_request_on_invalid_title(self):
        # Given: 유효하지 않은 Note title이 주어진다.
        invalid_title = ""
        invalid_request_body = {"title": invalid_title, "reason": "reason for note create"}
        # And: 로그인 해서 토큰을 발급받는다.
        user_token_of_creating_new_note = _login(self.user_data)

        # When: 인증이 필요한 Note Create API를 호출한다.
        response = self._call_note_create_api(invalid_request_body, user_token_of_creating_new_note)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Note는 생성되지 않는다.
        self.assertEqual(Note.objects.count(), 0)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_create_note_should_return_400_bad_request_on_invalid_reason(self):
        # Given: 유효하지 않는 Issue reason이 주어진다.
        invalid_reason = ""
        invalid_request_body = {"title": "test note title", "reason": invalid_reason}
        # And: 로그인 해서 토큰을 발급 받는다.
        user_token_of_creating_new_note = _login(self.user_data)

        # When: 인증이 필요한 Create Note API를 호출한다.
        response = self._call_note_create_api(invalid_request_body, user_token_of_creating_new_note)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Note는 생성되지 않는다.
        self.assertEqual(Note.objects.count(), 0)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_create_note_should_return_401_unauthorized_on_not_having_token_in_header(self):
        # Given: Note title과 Issue reason이 주어진다
        valid_request_body = {"title": "test note title", "reason": "reason for note create"}
        # And: 로그인은 하지 않는다.
        invalid_token = None

        # When: 인증이 필요한 Note Create API를 호출한다.
        response = self._call_note_create_api(valid_request_body, invalid_token)

        # Then: status code는 401을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # And: Note는 생성되지 않는다.
        self.assertEqual(Note.objects.count(), 0)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_should_change_field_of_is_approved_to_true_on_approving_issue_about_note_create(self):
        # Given: Note Create API를 호출하여 미승인 상태의 Note와 Note Create Issue를 생성한다.
        self._create_note_and_issue_by_calling_note_create_api()
        # And: Note Create Issue의 id가 주어진다.
        note_create_issue_id = Issue.objects.first().id
        # And: 해당 Issue에 권한을 가진 token을 발급 받는다.
        user_token_of_having_permission_to_issue_approve = _login(self.user_data)

        # When: Note Create Issue에 대한 Issue Approve API를 호출한다.
        response = self._call_issue_approve_api(note_create_issue_id, user_token_of_having_permission_to_issue_approve)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: Note의 is_approved가 True가 된다.
        note = Note.objects.first()
        self.assertTrue(note.is_approved)

    def test_should_not_change_field_of_is_approved_to_true_on_not_having_permission_to_issue_about_note_create(self):
        # Given: Note Create API를 호출하여 미승인 상태의 Note와 노트 생성 Issue를 생성한다.
        self._create_note_and_issue_by_calling_note_create_api()
        # And: Note Create Issue id가 주어진다.
        note_create_issue_id = Issue.objects.first().id
        # And: 해당 Issue에 권한이 없는 token을 발급 받는다.
        another_user_data = {"email": "test2@test.com", "password": "12345"}
        CtrlfUser.objects.create_user(**another_user_data)
        user_token_of_not_having_permission_to_issue_approve = _login(another_user_data)

        # When: Note Create Issue에 대한 Issue Approve API를 호출한다.
        response = self._call_issue_approve_api(
            note_create_issue_id, user_token_of_not_having_permission_to_issue_approve
        )

        # Then: status code는 403을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # And: Note의 is_approved는 그대로 False이다.
        note = Note.objects.first()
        self.assertFalse(note.is_approved)


class TestNoteDetail(NoteTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.note = self._make_note_list(1)[0]

    def _assert_note_detail_and_expected(self, actual, expected):
        self.assertEqual(actual["id"], expected.id)
        self.assertEqual(actual["title"], expected.title)
        self.assertEqual(actual["is_approved"], expected.is_approved)
        self.assertIn(expected.owners.first().id, actual["owners"])

    def test_note_detail_should_return_200_ok_and_note_detail_data(self):
        # Given: 유효한 Note id가 주어진다.
        valid_note_id = self.note.id

        # When: Note Detail API를 호출한다.
        response = self._call_note_detail_api(valid_note_id)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 응답 데이터에 필요한 정보들을 리턴한다.
        note = Note.objects.get(id=valid_note_id)
        self._assert_note_detail_and_expected(actual=response.data, expected=note)

    def test_note_detail_should_return_404_not_found_on_invalid_note_id(self):
        # Given: invalid Note id가 주어진다.
        invalid_note_id = 999

        # When: Note Detail API를 호출한다.
        response = self._call_note_detail_api(invalid_note_id)

        # Then : status code는 404이다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And : "노트를 찾을 수 없습니다."라는 메시지를 리턴한다.
        self.assertEqual(response.data["message"], "노트를 찾을 수 없습니다.")


class TestNoteUpdate(NoteTestMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.note = self._make_note_list(1)[0]

    def _create_issue_about_note_update_by_calling_note_update_api(self):
        note_update_request_body = {"new_title": "test new note title", "reason": "reason for note create"}
        user_token_of_creating_update_note_issue = _login(self.user_data)
        valid_note_id = self.note.id
        self._call_note_update_api(note_update_request_body, valid_note_id, user_token_of_creating_update_note_issue)

    def _assert_issue_about_update_note_and_expected(self, actual, expected):
        self.assertEqual(actual.title, expected["new_title"])
        self.assertEqual(actual.owner, self.user)
        self.assertEqual(actual.reason, expected["reason"])
        self.assertEqual(actual.status, CtrlfIssueStatus.REQUESTED)
        self.assertEqual(actual.related_model_type, CtrlfContentType.NOTE)
        self.assertEqual(actual.related_model_id, self.note.id)
        self.assertEqual(actual.action, CtrlfActionType.UPDATE)
        self.assertEqual(actual.etc, self.note.title)

    def test_update_note_should_return_200_ok_and_create_issue_about_note_update(self):
        # Given: 새로운 Note title과 Issue reason이 주어진다.
        valid_request_body = {
            "new_title": "test new note title",
            "reason": "reason for update note title",
        }
        # And: 로그인 해서 토큰을 발급받는다.
        user_token_of_creating_note_update_issue = _login(self.user_data)
        # And: 수정할 Note의 id가 주어진다.
        valid_note_id = self.note.id

        # When: 인증이 필요한 Note Update API를 호출한다.
        response = self._call_note_update_api(
            valid_request_body, valid_note_id, user_token_of_creating_note_update_issue
        )

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 생성된 Issue의 etc는 기존 Note의 title과 같고, Issue의 title은 new_title과 같다.
        issue = Issue.objects.first()
        self._assert_issue_about_update_note_and_expected(actual=issue, expected=valid_request_body)

    def test_update_note_should_return_404_not_found_on_invalid_note_id(self):
        # Given: 바꿀 note title과 reason이 주어진다.
        valid_request_body = {
            "new_title": "test new note title",
            "reason": "reason for update note title",
        }
        # And: 유효하지 않은 note id가 주어진다.
        invalid_note_id = 2342395
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받은 상황이다.
        user_token_of_creating_issue_about_note_update = _login(self.user_data)

        # When: 인증이 필요한 update note api를 호출한다.
        response = self._call_note_update_api(
            valid_request_body, invalid_note_id, user_token_of_creating_issue_about_note_update
        )

        # Then: status code는 404을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And: "노트를 찾을 수 없습니다."라는 메시지를 리턴한다.
        self.assertEqual(response.data["message"], "노트를 찾을 수 없습니다.")
        # And: Note Update에 대한 Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_update_note_should_return_400_bad_request_on_invalid_new_title(self):
        # Given: request body에 invalid title이 주어진다.
        invalid_title = ""
        invalid_request_body = {
            "new_title": invalid_title,
            "reason": "reason for update note title",
        }
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받은 상황이다.
        user_token_of_creating_issue_about_note_update = _login(self.user_data)
        # And: 수정할 Note의 id가 주어진다.
        valid_note_id = self.note.id

        # When: 인증이 필요한 Note Update API를 호출한다.
        response = self._call_note_update_api(
            invalid_request_body, valid_note_id, user_token_of_creating_issue_about_note_update
        )

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Then: Note Update에 대한 Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_update_note_should_return_400_bad_request_on_invalid_reason(self):
        # Given: request body에 invalid reason이 주어진다.
        invalid_reason = ""
        invalid_request_body = {
            "new_title": "test update note title",
            "reason": invalid_reason,
        }
        # And: 회원가입된 user 정보로 로그인을 해서 토큰을 발급받은 상황이다.
        user_token_of_creating_issue_about_note_update = _login(self.user_data)
        # And: 수정할 Note의 id가 주어진다.
        valid_note_id = self.note.id

        # When: 인증이 필요한 Note Update API를 호출한다.
        response = self._call_note_update_api(
            invalid_request_body, valid_note_id, user_token_of_creating_issue_about_note_update
        )

        # Then : status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Note Update에 대한 Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_update_note_should_return_401_unauthorized_on_not_having_token_in_header(self):
        # Given: 새로운 title과 reason이 주어진다.
        valid_request_body = {
            "new_title": "test update note title",
            "reason": "some reason for note update",
        }
        # And: 수정할 Note의 id가 주어진다.
        valid_note_id = self.note.id
        # And: 로그인을 하지 않은 상황
        token = None

        # When: 인증이 필요한 Note Update API를 호출한다.
        response = self._call_note_update_api(valid_request_body, valid_note_id, token)

        # Then: status code는 401을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # And: Note Update에 대한 Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_should_update_note_title_on_approving_issue_about_note_update(self):
        # Given: Note Update API를 호출하여 Note Update Issue를 생성한다.
        self._create_issue_about_note_update_by_calling_note_update_api()
        # And: Note Update Issue가 주어진다.
        valid_issue = Issue.objects.first()
        # And: 해당 Issue에 권한이 있는 user token을 발급받는다.
        issue_approve_user_token = _login(self.user_data)

        # When: Note Update Issue에 대한 Issue Approve API를 호출한다.
        response = self._call_issue_approve_api(valid_issue.id, issue_approve_user_token)

        # Then: status code는 200이다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: Note의 title이 업데이트 된다.
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, valid_issue.title)

    def test_should_not_update_note_title_on_not_having_permission_about_update_note_issue(self):
        # Given: Note Update API를 호출하여 Note Update Issue를 생성한다.
        self._create_issue_about_note_update_by_calling_note_update_api()
        # And: Note Update Issue가 주어진다.
        valid_issue = Issue.objects.first()
        # And: 해당 Issue에 권한이 없는 user의 토큰을 발급받는다.
        another_user_data = {"email": "test2@test.com", "password": "12345"}
        CtrlfUser.objects.create_user(**another_user_data)
        user_token_not_having_permission_to_issue = _login(another_user_data)

        # When: Note Update Issue에 대한 Issue Approve API를 호출한다.
        response = self._call_issue_approve_api(valid_issue.id, user_token_not_having_permission_to_issue)

        # Then: status code는 403이다.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # And: Note title은 업데이트 되지 않는다.
        note = Note.objects.get(id=self.note.id)
        self.assertNotEqual(note.title, valid_issue.title)


class TestNoteDelete(NoteTestMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.note = self._make_note_list(1)[0]

    def test_note_delete_on_success(self):
        # Given: 새로운 Note title과 Issue reason이 주어진다.
        valid_request_body = {
            "reason": "reason for delete note",
        }
        # And: 로그인 해서 토큰을 발급받는다.
        user_token_of_creating_note_delete_issue = _login(self.user_data)
        # And: 수정할 Note의 id가 주어진다.
        valid_note_id = self.note.id

        # When: Note 삭제 API를 호출 했을 떄
        self._call_note_delete_api(valid_request_body, valid_note_id, user_token_of_creating_note_delete_issue)

        # Then: Issue가 정상적으로 생성된다.
        issue = Issue.objects.first()
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(issue.title, f"{note.title} 삭제")
        self.assertEqual(issue.reason, valid_request_body["reason"])
        self.assertEqual(issue.owner.id, self.user.id)
        self.assertEqual(issue.status, CtrlfIssueStatus.REQUESTED)
        self.assertEqual(issue.related_model_type, CtrlfContentType.NOTE)
        self.assertEqual(issue.related_model_id, Note.objects.first().id)
        self.assertEqual(issue.action, CtrlfActionType.DELETE)

    def test_note_delete_on_fail_with_invalid_note_id(self):
        # Given: 새로운 Note title과 Issue reason이 주어진다.
        valid_request_body = {
            "reason": "reason for delete note",
        }
        # And: 로그인 해서 토큰을 발급받는다.
        user_token_of_creating_note_delete_issue = _login(self.user_data)
        # And: 유효하지 않은 수정할 Note의 id가 주어진다.
        invalid_note_id = 9999999

        # When: Note 삭제 API를 호출 했을 떄
        response = self._call_note_delete_api(
            valid_request_body, invalid_note_id, user_token_of_creating_note_delete_issue
        )

        # Then: status code는 404을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And: "노트를 찾을 수 없습니다."라는 메시지를 리턴한다.
        self.assertEqual(response.data["message"], "노트를 찾을 수 없습니다.")
        # Then: Issue가 생성되지 않아야 한다
        issue = Issue.objects.first()
        self.assertIsNone(issue)

    def test_should_delete_note_on_approving_issue_about_note_delete(self):
        # Given: Note Delete Issue를 생성한다
        note_delete_request_body = {"reason": "reason for note delete"}
        issue_data = {
            "owner": self.user.id,
            "title": f"{self.note.title} 삭제",
            "related_model_type": CtrlfContentType.NOTE,
            "action": CtrlfActionType.DELETE,
            "status": CtrlfIssueStatus.REQUESTED,
            "reason": note_delete_request_body["reason"],
        }
        issue_serializer = IssueCreateSerializer(data=issue_data)
        issue_serializer.is_valid(raise_exception=True)
        issue_serializer.save(related_model=self.note)
        # And: Note Delete Issue가 주어진다.
        valid_issue = Issue.objects.first()
        # And: 해당 Issue에 권한이 있는 user token을 발급받는다.
        issue_approve_user_token = _login(self.user_data)

        # When: Note Update Issue에 대한 Issue Approve API를 호출한다.
        response = self._call_issue_approve_api(valid_issue.id, issue_approve_user_token)

        # Then: status code는 204이다.
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # And: issue도 삭제되어야 한다
        valid_issue = Issue.objects.first()
        self.assertIsNone(valid_issue)
        # And: Note는 None 이어야 한다
        self.assertIsNone(Note.objects.filter(id=self.note.id).first())

    def test_should_not_delete_note_on_not_having_permission_about_delete_note_issue(self):
        # Given: Note Delete Issue를 생성한다
        note_delete_request_body = {"reason": "reason for note delete"}
        issue_data = {
            "owner": self.user.id,
            "title": f"{self.note.title} 삭제",
            "related_model_type": CtrlfContentType.NOTE,
            "action": CtrlfActionType.DELETE,
            "status": CtrlfIssueStatus.REQUESTED,
            "reason": note_delete_request_body["reason"],
        }
        issue_serializer = IssueCreateSerializer(data=issue_data)
        issue_serializer.is_valid(raise_exception=True)
        issue_serializer.save(related_model=self.note)
        # And: Note Delete Issue가 주어진다.
        valid_issue = Issue.objects.first()
        # And: 해당 Issue에 권한이 없는 user의 토큰을 발급받는다.
        another_user_data = {"email": "test2@test.com", "password": "12345"}
        CtrlfUser.objects.create_user(**another_user_data)
        user_token_not_having_permission_to_issue = _login(another_user_data)

        # When: Note Update Issue에 대한 Issue Approve API를 호출한다.
        response = self._call_issue_approve_api(valid_issue.id, user_token_not_having_permission_to_issue)

        # Then: status code는 403이다.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # And: Note는 삭제되지 않아야 한다.
        note = Note.objects.filter(id=self.note.id).first()
        self.assertIsNotNone(note)
