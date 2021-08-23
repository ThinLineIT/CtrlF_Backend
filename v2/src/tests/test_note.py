from ctrlf_auth.models import CtrlfUser
from ctrlf_auth.serializers import LoginSerializer
from ctrlfbe.models import Note
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status


class TestNoteList(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.data = {
            "email": "test@test.com",
            "password": "12345",
        }
        self.user = CtrlfUser.objects.create_user(**self.data)
        serializer = LoginSerializer()
        serialized = serializer.validate(self.data)
        self.token = serialized["token"]

    def _call_api(self, cursor):
        header = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        return self.client.get(reverse("notes:note_list_create"), {"cursor": cursor}, **header)

    def _make_notes(self, count):
        for i in range(0, count):
            note = Note.objects.create(title=f"test title {i}")
            note.owners.add(self.user)

    def test_retrieve_note_list_should_return_200(self):
        # Given: 미리 30개의 노트를 생성하고, 시작 cursor가 주어진다.
        self._make_notes(30)
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
        self._make_notes(10)
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


class TestNoteCreate(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.data = {
            "email": "test@test.com",
            "password": "12345",
        }
        self.user = CtrlfUser.objects.create_user(**self.data)

    def test_create_note_should_return_201(self):
        # Given: note title과 issue 내용이 주어진다
        request_body = {"title": "test note title", "content": "test issue content"}
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받은 상황이다.
        serializer = LoginSerializer()
        serialized = serializer.validate(self.data)
        token = serialized["token"]

        # When: 인증이 필요한 create note api를 호출한다.
        header = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        response = self.client.post(reverse("notes:note_list_create"), request_body, **header)

        # Then: status code는 201을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
