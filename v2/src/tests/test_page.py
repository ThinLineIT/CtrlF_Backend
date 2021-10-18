from ctrlf_auth.models import CtrlfUser
from ctrlf_auth.serializers import LoginSerializer
from ctrlfbe.models import Issue, Note, Page, Topic
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status


class TestPageCreate(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.data = {
            "email": "test@test.com",
            "password": "12345",
        }
        self.user = CtrlfUser.objects.create_user(**self.data)
        self.note = Note.objects.create(title="test note")
        self.note.owners.add(self.user)
        topic_data = {"note": self.note, "title": "test topic"}
        self.topic = Topic.objects.create(**topic_data)
        self.topic.owners.add(self.user)

    def _login(self):
        serializer = LoginSerializer()
        return serializer.validate(self.data)["token"]

    def _call_api(self, request_body, token=None):
        if token:
            header = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        else:
            header = {}
        return self.client.post(reverse("pages:page_create"), request_body, **header)

    def test_create_page_should_return_201(self):
        # Given: page title과 issue 내용이 주어진다
        request_body = {
            "title": "test page title",
            "content": "test issue content",
            "topic_id": 1,
            "summary": "summary",
        }
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받은 상황이다.
        token = self._login()

        # When: 인증이 필요한 create page api를 호출한다.
        response = self._call_api(request_body, token)

        # Then: status code는 201을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # And: Page가 정상적으로 생성된다.
        page = Page.objects.all()[0]
        self.assertEqual(page.title, "test page title")
        # And: Issue가 정상적으로 생성된다.
        issue = Issue.objects.all()[0]
        self.assertEqual(issue.content, "test issue content")
