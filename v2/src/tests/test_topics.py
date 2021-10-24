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
            "content": "test issue content on test topic",
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
        self.assertEqual(issue.content, "test issue content on test topic")
