from ctrlf_auth.models import CtrlfUser
from ctrlf_auth.serializers import LoginSerializer
from ctrlfbe.models import Note, Topic
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status


class TestTopicUpdate(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.topic_owner_data = {
            "email": "test@test.com",
            "password": "12345",
        }
        self.another_user_data = {
            "email": "test22@test.com",
            "password": "54321",
        }
        self.topic_owner = CtrlfUser.objects.create_user(**self.topic_owner_data)
        CtrlfUser.objects.create_user(**self.another_user_data)

    def _create_user(self, user_data):
        return CtrlfUser.objects.create_user(**user_data)

    def _create_topic(self, owner):
        self.note = Note.objects.create(title="test note title")
        self.note.owners.add(owner)
        self.topic = Topic.objects.create(note=self.note, title="test topic title")
        self.topic.owners.add(owner)

    def _login(self, user_data):
        serializer = LoginSerializer()
        return serializer.validate(user_data)["token"]

    def _call_api(self, request_body, token=None):
        if token:
            header = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        else:
            header = {}
        return self.client.put(
            reverse("topics:topic_update", kwargs={"topic_id": self.topic.id}),
            data=request_body,
            content_type="application/json",
            **header,
        )

    def test_should_return_200_when_topic_owner_approve_update(self):
        # Given: update topic title이 주어진다.
        request_body = {"title": "update topic title"}
        # And: topic을 생성한다.
        self._create_topic(self.topic_owner)
        # And: topic 생성한 계정으로 로그인 해서 token을 발급 받는다.
        token = self._login(user_data=self.topic_owner_data)

        # When: update topic api를 호출한다.
        response = self._call_api(request_body, token)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: message는 "수정되었습니다."를 리턴한다.
        self.assertEqual(response.data["message"], "수정되었습니다.")
        # And: 기존 topic의 title은 "update topic title"로 변경된다.
        self.assertEqual(Topic.objects.get(id=1).title, "update topic title")
