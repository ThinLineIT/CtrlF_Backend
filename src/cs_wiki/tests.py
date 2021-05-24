from django.test import TestCase
from django.urls import reverse

from cs_wiki.models import Issue, Note, Topic, Page


class TestIssuesList(TestCase):
    @staticmethod
    def _create_issue(expected):
        return Issue.objects.create(**expected)

    @staticmethod
    def _create_note(expected):
        return Note.objects.create(**expected)

    @staticmethod
    def _create_topic(expected):
        return Topic.objects.create(**expected)

    def test_issue_list(self):
        # Given: 노트 1개, 토픽 1개, 이슈 2개를 생성한다
        expected_1 = {
            "title": "운영체제",
        }
        note = self._create_note(expected_1)

        expected_2 = {
            "title": "스케줄러",
            "note_id": note,
        }
        topic = self._create_topic(expected_2)

        expected_3 = {
            "title": "test issue 1",
            "content": "test content 1",
            "note_id": note,
            "topic_id": topic,
        }
        expected_4 = {
            "title": "test issue 2",
            "content": "test content 2",
            "note_id": note,
            "topic_id": topic,
        }

        self._create_issue(expected_3)
        self._create_issue(expected_4)

        # When: Issue List API를 호출했을 때,
        response = self.client.get(reverse("cs_wiki:issue-list"))

        # Then: 길이는 2 이어야 한다.
        self.assertEqual(len(response.data), 2)


class TestNotesList(TestCase):
    @staticmethod
    def _create_note(expected):
        return Note.objects.create(**expected)

    def _call_api(self, search_value=""):
        return self.client.get(reverse("cs_wiki:note-list"), {"search": search_value})

    def test_note_list_with_filtering(self):
        # Given: 노트 2개를 생성한다
        expected_1 = {
            "title": "운영체제",
        }
        expected_2 = {
            "title": "test Note 2",
        }
        self._create_note(expected_1)
        self._create_note(expected_2)

        # When: Note List API 필터링과 함께 호출했을 때,
        response = self._call_api(search_value="운영체제")

        # Then: 길이는 1 이어야 한다.
        self.assertEqual(len(response.data), 1)

    def test_note_list_with_no_filtering(self):
        # Given: 노트 2개를 생성한다
        expected_1 = {
            "title": "운영체제",
        }
        expected_2 = {
            "title": "test Note 2",
        }
        self._create_note(expected_1)
        self._create_note(expected_2)

        # When: Note List API 필터링과 함께 호출했을 때, -> 조건에 아무것도 넣지 않음
        response = self._call_api()

        # Then: 길이는 2 이어야 한다.
        self.assertEqual(len(response.data), 2)


class TestPageDetail(TestCase):
    def setUp(self):
        self.note = Note.objects.create(title="test note")
        self.topic = Topic.objects.create(note_id=self.note, title="test topic")

    def _call_api(self, page_id):
        return self.client.get(
            reverse("cs_wiki:page-detail", kwargs={"page_id": page_id})
        )

    def test_page_detail(self):
        # Given: Page 1개를 생성한다.
        Page.objects.create(topic_id=self.topic, title="배열", content="배열이란 무엇인가?")

        # When: Page Detail API를 호출하면,
        response = self._call_api(page_id=1)

        # Then: 제목과 컨텐츠가 아래와 같이 나와야한다.
        self.assertEqual(response.data["title"], "배열")
        self.assertIn("배열이란 무엇인가?", response.data["content"])

    def test_page_detail_does_not_exist(self):
        # Given: Page 1개를 생성한다.
        Page.objects.create(topic_id=self.topic, title="배열", content="배열이란 무엇인가?")

        # When: Page Detail API를 호출할 때, 없는 page id를 호출하면,
        response = self._call_api(page_id=3)

        # Then: 404을 리턴해야한다
        self.assertEqual(response.status_code, 404)
