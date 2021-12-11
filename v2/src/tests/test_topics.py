import json

from ctrlf_auth.models import CtrlfUser
from ctrlf_auth.serializers import LoginSerializer
from ctrlfbe.models import Issue, Note, Topic
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status


class TestTopicList(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = CtrlfUser.objects.create_user(email="test@test.com", password="12345")
        self.note = Note.objects.create(title="test note")
        self.note.owners.add(self.user)

    def _add_topics_to_note(self, note, count):
        topic_list = []
        for i in range(count):
            topic_data = {"note": note, "title": f"test topic{i + 1} to {note.title}"}
            topic = Topic.objects.create(**topic_data)
            topic.owners.add(self.user)
            topic_list.append(topic)
        return topic_list

    def _call_api(self, note_id):
        return self.c.get(reverse("notes:topic_list", kwargs={"note_id": note_id}))

    def test_topic_list_should_return_200(self):
        # Given: 이미 저장된 topic들, 유효한 note id
        note_id = self.note.id
        topic_list = self._add_topics_to_note(note=self.note, count=10)
        # When : API 실행
        response = self._call_api(note_id)
        # Then : 상태코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And  : 이미 저장된 topic 개수와 같아야 함.
        response = response.data
        self.assertEqual(len(response), len(topic_list))

    def test_topic_list_should_return_topic_list_only_dependent_on_note_id(self):
        # Given: note A, B를 생성한다.
        note_A = Note.objects.create(title="note A")
        note_B = Note.objects.create(title="note B")
        # And: note A에 3개, note B에 5개의 topic을 생성한다.
        self._add_topics_to_note(note=note_A, count=3)
        self._add_topics_to_note(note=note_B, count=5)

        # When: note_A의 id로 topic list API 호출한다.
        response = self._call_api(note_A.id)

        # Then: status code는 200이다,
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: topic 개수는 3개이다.
        self.assertEqual(len(response.data), 3)

    def test_topic_list_should_return_200_by_empty_topic_list(self):
        # Given: 유효한 note id
        note_id = self.note.id
        # When : API 실행
        response = self._call_api(note_id)
        # Then : 상태코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And  : 빈 배열을 return 해야함.
        self.assertEqual(response.data, [])

    def test_topic_list_should_return_404_by_invalid_note_id(self):
        # Given: 이미 저장된 topic들, 유효하지 않은 note id
        invalid_not_id = 9999
        self._add_topics_to_note(note=self.note, count=10)
        # When : API 실행
        response = self._call_api(invalid_not_id)
        # Then : 상태코드 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And  : 메세지는 "노트를 찾을 수 없습니다." 이어야 함.
        response = response.data
        self.assertEqual(response["message"], "노트를 찾을 수 없습니다.")


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
        return self.client.post(reverse("topics:topic_create"), request_body, **header)

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


class TestTopicDetail(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = CtrlfUser.objects.create_user(email="test@test.com", password="12345")
        self.note = Note.objects.create(title="test note")
        self.note.owners.add(self.user)
        self.topic = Topic.objects.create(note=self.note, title="test topic")
        self.topic.owners.add(self.user)

    def test_topic_detail_should_return_200(self):
        # Given : 유효한 topic id, 이미 저장된 topic
        topic_id = self.topic.id
        # When  : API 실행
        response = self.c.get(reverse("topics:topic_detail_update", kwargs={"topic_id": topic_id}))
        # Then  : 상태코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And   : 불러온 정보가 저장된 정보와 일치해야 한다.
        response = response.data
        self.assertEqual(response["title"], "test topic")
        self.assertEqual(response["note"], self.note.id)

    def test_topic_detail_should_return_404_by_invalid_topic_id(self):
        # Given : 유효하지 않은 topic id, 이미 저장된 topic
        invalid_topic_id = 1234
        # When  : API 실행
        response = self.c.get(reverse("topics:topic_detail_update", kwargs={"topic_id": invalid_topic_id}))
        # Then  : 상태코드 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And   : 메세지는 "토픽을 찾을 수 없습니다." 이어야 한다.
        response = response.data
        self.assertEqual(response["message"], "토픽을 찾을 수 없습니다.")


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

    def _call_api(self, request_body, topic_id, token=None):
        if token:
            header = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        else:
            header = {}
        return self.client.put(
            reverse("topics:topic_detail_update", kwargs={"topic_id": topic_id}),
            json.dumps(request_body),
            content_type="application/json",
            **header,
        )

    def test_update_topic_should_return_200(self):
        # Given: 새로운 topic title과 reason이 주어질 때,
        request_body = {
            "new_title": "new topic title",
            "reason": "reason for topic update",
        }
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받은 상황
        token = self._login()

        # When: Topic update request api를 호출하면,
        response = self._call_api(request_body, self.topic.id, token)
        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: etc 값을 가지는 Issue가 생성되어야 한다
        issue = Issue.objects.all()[0]
        self.assertEqual(issue.title, "new topic title")
        self.assertEqual(issue.etc, self.topic.title)

    def test_update_topic_should_return_404_NOT_FOUND_on_topic_not_exist(self):
        # Given: 새로운 topic title과 reason이 주어질 때,
        request_body = {
            "new_title": "new topic title",
            "reason": "reason for topic update",
        }
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받은 상황
        token = self._login()
        # And: 존재하지 않는 토픽 id
        not_exist_topic_id = 1122334

        # When: 존재하지 않는 토픽id로 Topic update request api를 호출하면,
        response = self._call_api(request_body, not_exist_topic_id, token)

        # Then: status code는 404을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_topic_should_return_400_BAD_REQUEST_on_invalid_request_data(self):
        # Given: 새로운 topic title과 reason이 주어질 때,
        request_body = {
            "legacy_title": "new topic title",
            "reason": "reason for topic update",
            "useless_field": "useless field",
        }
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받은 상황
        token = self._login()

        # When: Topic update request api를 호출하면,
        response = self._call_api(request_body, self.topic.id, token)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
