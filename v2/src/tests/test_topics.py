from ctrlf_auth.models import CtrlfUser
from ctrlf_auth.serializers import LoginSerializer
from ctrlfbe.models import Issue, Note, Topic
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status


class TestTopicCreate(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.data = {
            "email": "test@test.com",
            "password": "12345",
        }
        self.user = CtrlfUser.objects.create_user(**self.data)
        self.note = Note.objects.create(title="basic note")
        self.note.owners.add(self.user)

    def _login(self):
        serializer = LoginSerializer()
        return serializer.validate(self.data)["token"]

    def _call_api(self, request_body, token=None):
        if token:
            header = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        else:
            header = {}
        return self.client.post(reverse("topics:topic_crete"), request_body, **header)

    def test_create_topic_should_return_201(self):
        # Given: topic title과 issue 내용이 주어진다
        request_body = {
            "note_id": self.note.id,
            "title": "test topic title",
            "reason": "reason for topic create",
        }
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받은 상황
        token = self._login()

        # When: 인증이 필요한 create topic api를 호출한다.
        response = self._call_api(request_body, token)

        # Then: status code는 201을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # And: Topic가 정상적으로 생성된다.
        topic = Topic.objects.all()[0]
        self.assertEqual(topic.title, "test topic title")
        # And: Issue가 정상적으로 생성된다.
        issue = Issue.objects.all()[0]
        self.assertEqual(issue.reason, "reason for topic create")

    def test_should_return_400_on_invalid_note_id(self):
        # Given: invalid한 note_id가 주어졌을 때
        invalid_note_id = 8954345
        request_body = {
            "note_id": invalid_note_id,
            "title": "test topic title",
            "reason": "reason for topic create",
        }
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받은 상황
        token = self._login()

        # When: 인증이 필요한 create topic api를 호출한다.
        response = self._call_api(request_body, token)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Topic은 생성되지 않는다.
        self.assertEqual(Topic.objects.count(), 0)
        # And: Issue도 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_should_return_401_on_unauthorized(self):
        # Given: topic title과 이슈 내용이 주어진다.
        request_body = {
            "note_id": self.note.id,
            "title": "test topic title",
            "reason": "reason for topic create",
        }

        # When: 인증이 필요한 create topic api를 호출한다.
        response = self._call_api(request_body)

        # Then: status code는 401을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # And: Topic은 생성되지 않는다.
        self.assertEqual(Topic.objects.count(), 0)
        # And: Issue도 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)


class TestTopicUpdate(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.data = {
            "email": "test@test.com",
            "password": "12345",
        }
        self.user = CtrlfUser.objects.create_user(**self.data)
        self.note = Note.objects.create(title="basic note")
        self.note.owners.add(self.user)
        topic_data = {"note": self.note, "title": "test topic"}
        self.topic = Topic.objects.create(**topic_data)
        self.topic.owners.add(self.user)

    def _login(self):
        serializer = LoginSerializer()
        return serializer.validate(self.data)["token"]

    def _call_api(self, request_body, topic, token=None):
        if token:
            header = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        else:
            header = {}
        return self.client.post(reverse("topics:topic_detail", kwargs={"topic_id": topic.id}), request_body, **header)

    def test_update_topic_should_return_200(self):
        # Given: 새로운 topic title과 reason이 주어질 때,
        request_body = {
            "new_title": "new topic title",
            "reason": "reason for topic update",
        }
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받은 상황
        token = self._login()

        # When: Topic update request api를 호출하면,
        response = self._call_api(request_body, self.topic, token)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: etc 값을 가지는 Issue가 생성되어야 한다
        issue = Issue.objects.all()[0]
        self.assertEqual(issue.title, "new topic title")
        self.assertEqual(issue.etc, self.topic.title)
