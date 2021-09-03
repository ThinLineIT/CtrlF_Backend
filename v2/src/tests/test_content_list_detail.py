from ctrlf_auth.models import CtrlfUser
from ctrlf_auth.serializers import LoginSerializer
from ctrlfbe.models import Issue, Note, Page, Topic
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status


class TestNoteDetail(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = CtrlfUser.objects.create_user(email="test@test.com", password="12345")
        self.note = Note.objects.create(title="test note")
        self.note.owners.add(self.user)

    def _call_api(self, note_id):
        return self.c.get(reverse("notes:note_detail_update_delete", kwargs={"note_id": note_id}))

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


class TestTopicList(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = CtrlfUser.objects.create_user(email="test@test.com", password="12345")
        self.note = Note.objects.create(title="test note")
        self.note.owners.add(self.user)

    def _add_topics(self):
        topic_list = []
        for i in range(10):
            topic_data = {"note": self.note, "title": f"test topic{i + 1}"}
            topic = Topic.objects.create(**topic_data)
            topic.owners.add(self.user)
            topic_list.append(topic)
        return topic_list

    def _call_api(self, note_id):
        return self.c.get(reverse("notes:topic_list", kwargs={"note_id": note_id}))

    def test_topic_list_should_return_200(self):
        # Given: 이미 저장된 topic들, 유효한 note id
        note_id = self.note.id
        topic_list = self._add_topics()
        # When : API 실행
        response = self._call_api(note_id)
        # Then : 상태코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And  : 이미 저장된 topic 개수와 같아야 함.
        response = response.data
        self.assertEqual(len(response), len(topic_list))

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
        self._add_topics()
        # When : API 실행
        response = self._call_api(invalid_not_id)
        # Then : 상태코드 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And  : 메세지는 "노트를 찾을 수 없습니다." 이어야 함.
        response = response.data
        self.assertEqual(response["message"], "노트를 찾을 수 없습니다.")


class TestPageList(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = CtrlfUser.objects.create_user(email="test@test.com", password="12345")
        self.note = Note.objects.create(title="test note")
        self.note.owners.add(self.user)
        topic_data = {"note": self.note, "title": "test topic"}
        self.topic = Topic.objects.create(**topic_data)
        self.topic.owners.add(self.user)

    def _add_pages(self):
        page_list = []
        for i in range(10):
            page_data = {"topic": self.topic, "title": f"test topic{i + 1}", "content": f"test content{i + 1}"}
            page = Page.objects.create(**page_data)
            page.owners.add(self.user)
            page_list.append(page)
        return page_list

    def _call_api(self, topic_id):
        return self.c.get(reverse("topics:page_list", kwargs={"topic_id": topic_id}))

    def test_page_list_should_return_200(self):
        # Given: 이미 저장된 page들, 유효한 topic id
        topic_id = self.topic.id
        page_list = self._add_pages()
        # When : API 실행
        response = self._call_api(topic_id)
        # Then : 상태코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And  : 이미 저장된 page 개수와 같아야 함.
        response = response.data
        self.assertEqual(len(response), len(page_list))

    def test_page_list_should_return_200_by_empty_page_list(self):
        # Given: 유효한 topic id
        topic_id = self.topic.id
        # When : API 실행
        response = self._call_api(topic_id)
        # Then : 상태코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And  : 빈 배열을 return 해야함.
        self.assertEqual(response.data, [])

    def test_page_list_should_return_404_by_invalid_topic_id(self):
        # Given: 이미 저장된 page들, 유효하지 않은 topic id
        invalid_topic_id = 9999
        self._add_pages()
        # When : API 실행
        response = self._call_api(invalid_topic_id)
        # Then : 상태코드 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And  : 메세지는 "토픽을 찾을 수 없습니다." 이어야 함.
        response = response.data
        self.assertEqual(response["message"], "토픽을 찾을 수 없습니다.")


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
        response = self.c.get(reverse("topics:topic_detail", kwargs={"topic_id": topic_id}))
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
        response = self.c.get(reverse("topics:topic_detail", kwargs={"topic_id": invalid_topic_id}))
        # Then  : 상태코드 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And   : 메세지는 "토픽을 찾을 수 없습니다." 이어야 한다.
        response = response.data
        self.assertEqual(response["message"], "토픽을 찾을 수 없습니다.")


class TestPageDetail(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = CtrlfUser.objects.create_user(email="test@test.com", password="12345")
        self.note = Note.objects.create(title="test note")
        self.note.owners.add(self.user)
        self.topic = Topic.objects.create(note=self.note, title="test topic")
        self.topic.owners.add(self.user)
        page_data = {"topic": self.topic, "title": "test page", "content": "test content"}
        self.page = Page.objects.create(**page_data)
        self.page.owners.add(self.user)

    def test_page_detail_should_return_200(self):
        # Given : 유효한 page id, 이미 저장된 page
        page_id = self.page.id
        # When  : API 실행
        response = self.c.get(reverse("pages:page_detail", kwargs={"page_id": page_id}))
        # Then  : 상태코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And   : 불러온 정보가 저장된 정보와 일치해야 한다.
        response = response.data
        self.assertEqual(response["title"], "test page")
        self.assertEqual(response["content"], "test content")
        self.assertEqual(response["topic"], self.topic.id)

    def test_page_detail_should_return_404_by_invalid_page_id(self):
        # Given : 유효하지 않은 page id, 이미 저장된 page
        invalid_page_id = 1234
        # When  : API 실행
        response = self.c.get(reverse("pages:page_detail", kwargs={"page_id": invalid_page_id}))
        # Then  : 상태코드 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And   : 메세지는 "페이지를 찾을 수 없습니다." 이어야 한다.
        response = response.data
        self.assertEqual(response["message"], "페이지를 찾을 수 없습니다.")


class TestTopicCreate(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.data = {
            "email": "test@test.com",
            "password": "12345",
        }
        self.user = CtrlfUser.objects.create_user(**self.data)

    def _login(self):
        serializer = LoginSerializer()
        return serializer.validate(self.data)["token"]

    def _call_api(self, request_body, token=None):
        if token:
            header = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        else:
            header = {}
        return self.client.post(reverse("topics:topic_create"), request_body, **header)

    def make_note(self):
        self.note = Note.objects.create(title="test note title")
        self.note.owners.add(self.user)

    def test_topic_create_should_return_201(self):
        # Given: 미리 생성된 노트, 로그인 하여 얻은 토큰, 유효한 토픽 생성 정보.
        self.make_note()
        token = self._login()
        request_body = {"note": self.note.id, "title": "test title", "content": "test issue content"}

        # When : API 실행.
        response = self._call_api(request_body, token=token)

        # Then : 상태코드 201이어야 함.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # And : 생성된 토픽 정보가 일치해야 한다.
        topic = Topic.objects.all()[0]
        self.assertEqual(topic.note, self.note)
        self.assertEqual(topic.title, "test title")

        # And : 생성된 이슈 정보와 일치해야 한다.
        issue = Issue.objects.all()[0]
        self.assertEqual(issue.title, "test title")
        self.assertEqual(issue.content, "test issue content")

    def test_topic_create_should_return_401_without_login(self):
        # Given: 미리 생성된 노트, 로그인 하여 얻은 토큰, 유효한 토픽 생성 정보
        self.make_note()
        request_body = {"note": self.note.id, "title": "test title", "content": "test issue content"}

        # When : API 실행
        response = self._call_api(request_body)

        # Then : 상태코드 401이어야 함.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_topic_create_should_return_404_by_invalid_note_id(self):
        # Given: 미리 생성된 노트, 로그인 하여 얻은 토큰, 유효하지 않은 노트 ID.
        self.make_note()
        token = self._login()
        invalid_note_id = 1234
        request_body = {"note": invalid_note_id, "title": "test title", "content": "test issue content"}

        # When : API 실행.
        response = self._call_api(request_body, token=token)

        # Then : 상태코드 404이어야 함.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # And : 메세지는 노트를 찾을 수 없습니다. 이어야 함.
        response = response.data
        self.assertEqual(response["message"], "노트를 찾을 수 없습니다.")

    def test_topic_create_should_return_400_without_title(self):
        # Given: 미리 생성된 노트, 로그인 하여 얻은 토큰, title 없음.
        self.make_note()
        token = self._login()
        request_body = {"note": self.note.id, "content": "test issue content"}

        # When : API 실행.
        response = self._call_api(request_body, token=token)

        # Then : 상태코드 400이어야 함.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # And : 메세지는 title을(를) 입력하세요. 이어야 함.
        response = response.data
        self.assertEqual(response["message"], "title을(를) 입력하세요.")

    def test_topic_create_should_return_400_without_content(self):
        # Given: 미리 생성된 노트, 로그인 하여 얻은 토큰, content 없음.
        self.make_note()
        token = self._login()
        request_body = {"note": self.note.id, "title": "test title"}

        # When : API 실행.
        response = self._call_api(request_body, token=token)

        # Then : 상태코드 400이어야 함.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # And : 메세지는 content을(를) 입력하세요. 이어야 함.
        response = response.data
        self.assertEqual(response["message"], "content을(를) 입력하세요.")
