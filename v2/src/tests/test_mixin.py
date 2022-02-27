from ctrlf_auth.models import CtrlfUser
from ctrlf_auth.serializers import LoginSerializer
from ctrlfbe.models import (
    CtrlfActionType,
    CtrlfContentType,
    CtrlfIssueStatus,
    Issue,
    Note,
    Page,
    PageHistory,
    PageVersionType,
    Topic,
)
from django.test import Client


def _login(user_data):
    return LoginSerializer().validate(user_data)["token"]


def _get_header(token):
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"} if token else {}


class IssueTestMixin:
    def setUp(self) -> None:
        self.client = Client()
        self.user_data = {
            "email": "test@test.com",
            "password": "12345",
        }
        self.user = CtrlfUser.objects.create_user(**self.user_data)

        self.owner_data = {
            "email": "jinho@naver.com",
            "password": "q1w2e3r4",
        }
        self.owner = CtrlfUser.objects.create_user(**self.owner_data)
        self.note = Note.objects.create(title="basic note")
        topic_data = {"note": self.note, "title": "basic topic"}
        self.topic = Topic.objects.create(**topic_data)

    def _make_note(self):
        note = Note.objects.create(title="test note title")
        note.owners.add(self.owner)
        issue_data = {
            "owner": self.owner,
            "title": "test note title",
            "reason": "reason for note create",
            "status": CtrlfIssueStatus.REQUESTED,
            "related_model_type": CtrlfContentType.NOTE,
            "related_model_id": note.id,
            "action": CtrlfActionType.CREATE,
        }
        issue = Issue.objects.create(**issue_data)
        return note.id, issue.id

    def _make_topic(self):
        topic_data = {"note": self.note, "title": "test topic title"}
        topic = Topic.objects.create(**topic_data)
        topic.owners.add(self.owner)
        issue_data = {
            "owner": self.owner,
            "title": "test topic title",
            "reason": "reason for topic create",
            "status": CtrlfIssueStatus.REQUESTED,
            "related_model_type": CtrlfContentType.TOPIC,
            "related_model_id": topic.id,
            "action": CtrlfActionType.CREATE,
        }
        issue = Issue.objects.create(**issue_data)
        return topic.id, issue.id

    def _make_page(self):
        page = Page.objects.create(topic=self.topic)
        page.owners.add(self.owner)
        page_history_data = {
            "owner": self.user,
            "page": page,
            "title": "test page title",
            "content": "test page content",
            "version_type": PageVersionType.CURRENT,
        }
        page_history = PageHistory.objects.create(**page_history_data)
        issue_data = {
            "owner": self.owner,
            "title": "test page title",
            "reason": "reason for page create",
            "status": CtrlfIssueStatus.REQUESTED,
            "related_model_type": CtrlfContentType.PAGE,
            "related_model_id": page.id,
            "action": CtrlfActionType.CREATE,
        }
        issue = Issue.objects.create(**issue_data)
        return page, issue, page_history

    def _login(self, user_data):
        serializer = LoginSerializer()
        return serializer.validate(user_data)["token"]

    def _get_issue_list(self):
        _, page_issue, _ = self._make_page()
        topic_issue_id, _ = self._make_topic()
        note_issue_id, _ = self._make_note()
        topic_issue = Issue.objects.get(id=topic_issue_id)
        note_issue = Issue.objects.get(id=note_issue_id)

        return [page_issue, topic_issue, note_issue]
