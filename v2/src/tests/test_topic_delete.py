from ctrlf_auth.models import CtrlfUser
from ctrlf_auth.serializers import LoginSerializer
from ctrlfbe.models import Note, Topic
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status


class TestTopicDelete(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.topic_owner_data = {
            "email": "test@test.com",
            "password": "12345",
        }
        self.another_user_data = {
            "email": "testtest2@test.com",
            "password": "54321",
        }
        self.topic_owner = CtrlfUser.objects.create_user(**self.topic_owner_data)
        CtrlfUser.objects.create_user(**self.another_user_data)

    def _create_topic(self, owner):
        note = Note.objects.create(title="test note title")
        note.owners.add(owner)
        self.topic = Topic.objects.create(note=note, title="test topic title")
        self.topic.owners.add(owner)

    def _login(self, user_data):
        serializer = LoginSerializer()
        return serializer.validate(user_data)["token"]

    def _call_api(self, token=None):
        if token:
            header = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        else:
            header = {}
        return self.client.delete(reverse("topics:topic_delete", kwargs={"topic_id": self.topic.id}), **header)

    def test_should_return_204_when_topic_owner_approve_delete(self):
        # Given: Topic을 생성한다.
        self._create_topic(self.topic_owner)
        # And: Topic을 생성한 계정으로 로그인하여 토큰을 발급받는다.
        owner_token = self._login(self.topic_owner_data)

        # When: delete topic api를 호출한다.
        response = self._call_api(owner_token)

        # Then: status code 204을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # And: Topic count는 0이다.
        self.assertEqual(Topic.objects.count(), 0)
        # And: message로 "삭제 되었습니다."를 리턴한다.
        self.assertEqual(response.data["message"], "삭제 되었습니다.")
