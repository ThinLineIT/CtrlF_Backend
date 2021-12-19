import json

from ctrlf_auth.models import CtrlfUser
from ctrlf_auth.serializers import LoginSerializer
from ctrlfbe.models import Issue, Note
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status


class TestNoteBase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user_data = {
            "email": "test@test.com",
            "password": "12345",
        }
        self.user = CtrlfUser.objects.create_user(**self.user_data)

    def _login(self, user_data):
        serializer = LoginSerializer()
        return serializer.validate(user_data)["token"]

    def _make_note_list(self, count):
        note_list = []
        for i in range(count):
            note = Note.objects.create(title=f"test title {i + 1}")
            note.owners.add(self.user)
            note_list.append(note)

        return note_list


class TestNoteList(TestNoteBase):
    def _call_api(self, cursor):
        return self.client.get(reverse("notes:note_list_create"), {"cursor": cursor})

    def test_retrieve_note_list_should_return_200(self):
        # Given: 미리 30개의 노트를 생성하고, 시작 cursor가 주어진다.
        self._make_note_list(30)
        given_cursor = 0

        # When: retrieve note list api를 호출한다.
        response = self._call_api(given_cursor)

        # Then: status code 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: next_cursor는 30을 리턴한다.
        self.assertEqual(response.data["next_cursor"], 30)
        # And: 시작 cursor부터 30개의 note list를 리턴한다.
        self.assertEqual(len(response.data["notes"]), 30)

    def test_retrieve_note_list_on_note_count_less_than_30(self):
        # Given: 10개의 note를 생성하고 시작 cursor를 0으로 주어진다.
        self._make_note_list(10)
        given_cursor = 3

        # When: retrieve note list api를 호출한다.
        response = self._call_api(given_cursor)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: next_cursor는 10을 리턴한다.
        self.assertEqual(response.data["next_cursor"], 10)
        # And: 시작 cursor부터 7개의 note list를 리턴한다.
        self.assertEqual(len(response.data["notes"]), 7)

    def test_retrieve_note_list_on_no_note(self):
        # Given: 노트 생성 없이, cursor만 주어진다.
        given_cursor = 0

        # When: retrieve note list api를 호풀한다.
        response = self._call_api(given_cursor)

        # Then: status code는 200을 리턴한다
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: next_cursor는 0을 리턴한다.
        self.assertEqual(response.data["next_cursor"], 0)
        # And: empty list를 리턴한다.
        self.assertEqual(len(response.data["notes"]), 0)


class TestNoteCreate(TestNoteBase):
    def _call_api(self, request_body, token=None):
        if token:
            header = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        else:
            header = {}
        return self.client.post(reverse("notes:note_list_create"), request_body, **header)

    def test_create_note_should_return_201(self):
        # Given: note title과 issue 내용이 주어진다
        request_body = {"title": "test note title", "reason": "reason for note create"}
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받은 상황이다.
        token = self._login(self.user_data)

        # When: 인증이 필요한 create note api를 호출한다.
        response = self._call_api(request_body, token)

        # Then: status code는 201을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # And: Note가 정상적으로 생성된다.
        note = Note.objects.all()[0]
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(note.title, "test note title")
        # And: Issue가 정상적으로 생성된다.
        issue = Issue.objects.all()[0]
        self.assertEqual(Issue.objects.count(), 1)
        self.assertEqual(issue.reason, "reason for note create")

    def test_create_note_should_return_401_when_not_login(self):
        # Given: note title과 issue 내용이 주어진다, 로그인은 하지 않는다.
        request_body = {"title": "test note title", "reason": "reason for note create"}

        # When: 인증이 필요한 create note api를 호출한다.
        response = self._call_api(request_body)

        # Then: status code는 401을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # And: Note와 Issue는 생성되지 않는다.
        self.assertEqual(Note.objects.count(), 0)
        self.assertEqual(Issue.objects.count(), 0)

    def test_create_note_should_return_400_when_invalid_title(self):
        # Given: invalid title과 valid한 이슈 내용이 주어진다.
        invalid_title = ""
        request_body = {"title": invalid_title, "reason": "reason for note create"}
        # And: 로그인 해서 토큰을 발급받은 상황이다.
        token = self._login(self.user_data)

        # When: 인증이 필요한 create note api를 호출한다.
        response = self._call_api(request_body, token)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Note와 Issue는 생성되지 않는다.
        self.assertEqual(Note.objects.count(), 0)
        self.assertEqual(Issue.objects.count(), 0)

    def test_create_note_should_return_400_when_invalid_content(self):
        # Given: valid한 title과 invalid한 이슈 내용이 주어진다.
        invalid_issue_reason = ""
        request_body = {"title": "test title", "reason": invalid_issue_reason}
        # And: 로그인 해서 토큰을 발급받은 상황이다.
        token = self._login(self.user_data)

        # When: 인증이 필요한 create note api를 호출한다.
        response = self._call_api(request_body, token)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Note와 Issue는 생성되지 않는다.
        self.assertEqual(Note.objects.count(), 0)
        self.assertEqual(Issue.objects.count(), 0)


class TestNoteDetail(TestNoteBase):
    def setUp(self):
        super().setUp()
        self.note = self._make_note_list(1)[0]

    def _call_api(self, note_id):
        return self.client.get(reverse("notes:note_detail_update_delete", kwargs={"note_id": note_id}))

    def test_note_detail_should_return_200(self):
        # Given: 정상적인 note id
        note_id = self.note.id
        # When : API 실행
        response = self._call_api(note_id)
        # Then : 상태코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And  : 미리 생성했던 정보와 일치해야 함.
        data = response.data
        self.assertEqual(data["id"], note_id)
        self.assertEqual(data["title"], self.note.title)
        self.assertEqual(data["is_approved"], self.note.is_approved)
        self.assertIn(self.user.id, data["owners"])

    def test_note_detail_should_return_404_by_invalid_note_id(self):
        # Given : 존재하지 않는 note id
        invalid_note_id = 999
        # When : API 실행
        response = self._call_api(invalid_note_id)
        # Then : 상태코드 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And  : 메세지는 "노트를 찾을 수 없습니다." 이어야 함.
        self.assertEqual(response.data["message"], "노트를 찾을 수 없습니다.")


class TestNoteUpdate(TestNoteBase):
    def setUp(self) -> None:
        super().setUp()
        self.note = self._make_note_list(1)[0]

    def _call_api(self, request_body, note_id, token=None):
        if token:
            header = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        else:
            header = {}
        return self.client.put(
            reverse("notes:note_detail_update_delete", kwargs={"note_id": note_id}),
            data=json.dumps(request_body),
            content_type="application/json",
            **header,
        )

    def test_update_note_should_return_200_and_create_issue_about_note_update(self):
        # Given: 바꿀 note title과 reason이 주어진다.
        request_body = {
            "new_title": "test new note title",
            "reason": "reason for update note title",
        }
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받은 상황이다.
        token = self._login(self.user_data)

        # When: 인증이 필요한 update note api를 호출한다.
        response = self._call_api(request_body, self.note.id, token)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: Issue가 생성되고, Issue의 etc는 Note의 title과 같고, Issue의 title은 new_title과 같다.
        issue = Issue.objects.first()
        self.assertEqual(issue.etc, self.note.title)
        self.assertEqual(issue.title, "test new note title")

    def test_update_note_should_return_404_on_invalid_note_id(self):
        # Given: 바꿀 note title과 reason이 주어진다.
        request_body = {
            "new_title": "test new note title",
            "reason": "reason for update note title",
        }
        # And: 유효하지 않은 note id가 주어진다.
        invalid_note_id = 2342395
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받은 상황이다.
        token = self._login(self.user_data)

        # When: 인증이 필요한 update note api를 호출한다.
        response = self._call_api(request_body, invalid_note_id, token)

        # Then: status code는 404을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_should_return_400_on_invalid_request_key(self):
        # Given: request body에 invalid data가 주어진다.
        request_body = {
            "invalid_key": "invalid",
            "reason": "reason for update note title",
        }
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받은 상황이다.
        token = self._login(self.user_data)

        # When: 인증이 필요한 update note api를 호출한다.
        response = self._call_api(request_body, self.note.id, token)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
