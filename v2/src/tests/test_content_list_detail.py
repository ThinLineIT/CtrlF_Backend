from ctrlf_auth.models import CtrlfUser
from ctrlfbe.models import (
    ContentRequest,
    CtrlfActionType,
    CtrlfContentType,
    CtrlfIssueStatus,
    Issue,
    Note,
    Page,
    Topic,
)
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

    def test_page_list_should_have_issue_id(self):
        # Given: 유효한 topic_id를 설정하고,
        valid_topic_id = self.topic.id
        # And: page를 생성한다
        page_list = self._add_pages()
        # And: content request를 생성하고,
        content_request = ContentRequest.objects.create(
            user=self.user, sub_id=page_list[0].id, type=CtrlfContentType.PAGE, action=CtrlfActionType.CREATE
        )
        # And: 해당 Page에 대한 Issue를 생성하고,
        Issue.objects.create(
            owner=self.user,
            title="page issue",
            content="page issue content",
            status=CtrlfIssueStatus.APPROVED,
            content_request=content_request,
        )

        # When: API를 실행 했을 때,
        response = self._call_api(valid_topic_id)

        # Then: issue_id가 응답 값 내에 있어야 하고,
        self.assertIn("issue_id", response.data[0])
        # And: page에 해당하는 issue_id 이어야 한다
        self.assertEqual(response.data[0]["issue_id"], 1)

    def test_page_list_should_have_issue_id_but_value_is_none(self):
        # Given: 유효한 topic_id를 설정하고,
        valid_topic_id = self.topic.id
        # And: page를 생성하고,
        self._add_pages()
        # And: 해당하는 issue가 없는 상태에서

        # When: API를 실행 했을 때,
        response = self._call_api(valid_topic_id)

        # Then: issue_id가 응답 값 내에 있어야 하고,
        self.assertIn("issue_id", response.data[0])
        # And: page에 해당하는 issue_id는 None 이어야 한다
        self.assertIsNone(response.data[0]["issue_id"])


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
