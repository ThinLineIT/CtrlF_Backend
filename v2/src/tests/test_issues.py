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
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status


class IssueTextMixin:
    def setUp(self) -> None:
        self.client = Client()
        self.user_data = {
            "email": "test@test.com",
            "password": "12345",
        }
        self.user = CtrlfUser.objects.create_user(**self.user_data)

    def _call_api(self, cursor):
        return self.client.get(
            reverse("issues:issue_list"),
            {"cursor": cursor},
        )

    def _call_detail_api(self, issue_id):
        return self.client.get(reverse("issues:issue_detail", kwargs={"issue_id": issue_id}))

    def _make_issues(self, count):
        for i in range(1, count + 1):
            Issue.objects.create(
                owner=self.user,
                title=f"test title {i}",
                reason=f"reason for note or topic or page crud {i}",
                status=CtrlfIssueStatus.REQUESTED,
                related_model_type=CtrlfContentType.NOTE,
                related_model_id=1,
                action=CtrlfActionType.CREATE,
            )

    def _make_issues_by_status(self, title: str, reason: str, status: CtrlfIssueStatus):
        Issue.objects.create(
            owner=self.user,
            title="test title",
            reason="reason for note or topic or page crud",
            status=status,
            related_model_type=CtrlfContentType.NOTE,
            related_model_id=1,
            action=CtrlfActionType.CREATE,
        )

    def _make_all_contents(self):
        self.note = Note.objects.create(title="test note")
        self.note.owners.add(self.user)
        self.topic = Topic.objects.create(note=self.note, title="test topic")
        self.topic.owners.add(self.user)
        self.page = Page.objects.create(topic=self.topic)
        self.page.owners.add(self.user)

        page_history_data = {
            "owner": self.user,
            "page": self.page,
            "title": "test page",
            "content": "test content",
            "version_type": PageVersionType.CURRENT,
        }

        self.page_history = PageHistory.objects.create(**page_history_data)
        return self.note, self.topic, self.page, self.page_history


class TestListIssue(IssueTextMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_issue_list_should_return_200(self):
        # Given: 미리 30개의 이슈를 생성하고, 시작 cursor가 주어진다.
        self._make_issues(30)
        given_cursor = 0

        # When: issue list api를 호출한다.
        response = self._call_api(given_cursor)

        # Then: status code 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: next_cursor는 30을 리턴한다.
        self.assertEqual(response.data["next_cursor"], 30)
        # And: 시작 cursor부터 30개의 issue list를 리턴한다.
        self.assertEqual(len(response.data["issues"]), 30)

    def test_issue_list_on_issue_count_less_than_30(self):
        # Given: 10개의 이슈를 생성하고 시작 cursor를 3으로 주어진다.
        self._make_issues(10)
        given_cursor = 3

        # When: issue list api를 호출한다.
        response = self._call_api(given_cursor)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: next_cursor는 10을 리턴한다.
        self.assertEqual(response.data["next_cursor"], 10)
        # And: 시작 cursor부터 7개의 issue list를 리턴한다.
        self.assertEqual(len(response.data["issues"]), 7)

    def test_issue_list_on_empty_issue(self):
        # Given: 이슈 생성 없이, cursor만 주어진다.
        given_cursor = 0

        # When: issue list api를 호풀한다.
        response = self._call_api(given_cursor)

        # Then: status code는 200을 리턴한다
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: next_cursor는 0을 리턴한다.
        self.assertEqual(response.data["next_cursor"], 0)
        # And: empty list를 리턴한다.
        self.assertEqual(len(response.data["issues"]), 0)

    def test_issue_list_should_return_200_on_filtering(self):
        # Given: 미리 4개의 이슈를 생성하고, 시작 cursor가 주어진다.
        self._make_issues_by_status(title="test1", reason="reasons1", status=CtrlfIssueStatus.REQUESTED)
        self._make_issues_by_status(title="test2", reason="reasons2", status=CtrlfIssueStatus.APPROVED)
        self._make_issues_by_status(title="test3", reason="reasons3", status=CtrlfIssueStatus.CLOSED)
        self._make_issues_by_status(title="test4", reason="reasons4", status=CtrlfIssueStatus.REJECTED)
        given_cursor = 0

        # When: issue list api를 호출한다.
        response = self._call_api(given_cursor)

        # Then: status code 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 이슈의 개수는 2개이어야 한다 -> REQUESTED, REJECTED
        self.assertEqual(len(response.data["issues"]), 2)
        # And: 이슈 status는 REQUESTED or REJECTED 이어야 한다
        for issue in response.data["issues"]:
            self.assertIn(issue["status"], {CtrlfIssueStatus.REQUESTED, CtrlfIssueStatus.REJECTED})


class TestIssueDetail(IssueTextMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_issue_detail_should_return_issue_on_success(self):
        # Given: Issue에 해당하는 컨텐츠들을 생성한다
        note, topic, page, page_history = self._make_all_contents()
        # And: page 생성에 대한 컨텐트 요청을 생성하고
        # And: 이슈를 1개 생성 하였을 때,
        issue = Issue.objects.create(
            owner=self.user,
            title="test issue title",
            reason="reason for create page",
            status=CtrlfIssueStatus.REQUESTED,
            related_model_type=CtrlfContentType.PAGE,
            related_model_id=self.page_history.id,
            action=CtrlfActionType.CREATE,
            etc="legacy title",
        )

        # When: issue detail api를 호출한다.
        response = self._call_detail_api(issue_id=issue.id)

        # Then: status code는 200을 리턴한다
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 생성된 이슈와 값이 일치해야한다
        self.assertEqual(response.data["title"], "test issue title")
        self.assertEqual(response.data["reason"], "reason for create page")
        self.assertEqual(response.data["status"], CtrlfIssueStatus.REQUESTED)
        self.assertEqual(response.data["owner"], self.user.email)

        # And: issue에 대한 note, topic, page의 id를 제공해야한다
        self.assertEqual(response.data["note_id"], self.note.id)
        self.assertEqual(response.data["topic_id"], self.topic.id)
        self.assertEqual(response.data["page_id"], self.page.id)

    def test_issue_detail_should_return_404_not_found_on_issue_does_not_exist(self):
        # Given: 이슈를 생성하지 않았을 때,
        invalid_issue_id = 1122334

        # When: issue list api를 호출한다.
        response = self._call_detail_api(issue_id=invalid_issue_id)

        # Then: status code는 404을 리턴한다
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestIssueApprove(IssueTextMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.owner_data = {
            "email": "jinho@naver.com",
            "password": "q1w2e3r4",
        }
        self.owner = CtrlfUser.objects.create_user(**self.owner_data)
        self.note = Note.objects.create(title="basic note")
        self.note.owners.add(self.owner)
        topic_data = {"note": self.note, "title": "basic topic"}
        self.topic = Topic.objects.create(**topic_data)
        self.topic.owners.add(self.owner)

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

    def _call_api(self, request_body, token=None):
        if token:
            header = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        else:
            header = {}
        return self.client.post(reverse("actions:issue_approve"), request_body, **header)

    def test_issue_approve_should_return_200_on_issue_about_note(self):
        # Given: Note와 Issue를 생성한다.
        note_id, issue_id = self._make_note()
        # And: request_body로 유효한 issue id가 주어진다.
        request_body = {"issue_id": issue_id}
        # And: owner 정보로 로그인 하여 토큰을 발급받은 상태이다.
        owner_token = self._login(self.owner_data)

        # When: 인증이 필요한 approve issue api를 호출한다.
        response = self._call_api(request_body, owner_token)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: "승인 완료"라는 메세지를 리턴한다
        self.assertEqual(response.data["message"], "승인 완료")
        # And: Note의 is_apporved는 True이다.
        note = Note.objects.get(id=note_id)
        self.assertTrue(note.is_approved)
        # And: Issue의 status는 APPROVED이다.
        issue = Issue.objects.get(id=issue_id)
        self.assertEqual(issue.status, CtrlfIssueStatus.APPROVED)

    def test_issue_approve_should_return_200_on_issue_about_topic(self):
        # Given: Topic과 Issue를 생성한다.
        topic_id, issue_id = self._make_topic()
        # And: request_body로 유효한 issue id가 주어진다.
        request_body = {"issue_id": issue_id}
        # And: owner 정보로 로그인 하여 토큰을 발급받은 상태이다.
        owner_token = self._login(self.owner_data)

        # When: 인증이 필요한 approve issue api를 호출한다.
        response = self._call_api(request_body, owner_token)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: "승인 완료"라는 메세지를 리턴한다
        self.assertEqual(response.data["message"], "승인 완료")
        # And: Topic의 is_apporved는 True이다.
        topic = Topic.objects.get(id=topic_id)
        self.assertTrue(topic.is_approved)
        # And: Issue의 status는 APPROVED이다.
        issue = Issue.objects.get(id=issue_id)
        self.assertEqual(issue.status, CtrlfIssueStatus.APPROVED)

    def test_issue_approve_should_return_200_on_issue_about_page(self):
        # Given: Page와 Issue를 생성한다.
        page, issue, page_history = self._make_page()
        # And: request_body로 유효한 issue id가 주어진다.
        request_body = {"issue_id": issue.id}
        # And: owner 정보로 로그인 하여 토큰을 발급받은 상태이다.
        owner_token = self._login(self.owner_data)

        # When: 인증이 필요한 approve issue api를 호출한다.
        response = self._call_api(request_body, owner_token)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: "승인 완료"라는 메세지를 리턴한다
        self.assertEqual(response.data["message"], "승인 완료")
        # And: PageHistory의 is_apporved는 True이다.
        result = PageHistory.objects.get(id=page_history.id)
        self.assertTrue(result.is_approved)
        # And: Issue의 status는 APPROVED이다.
        issue = Issue.objects.get(id=issue.id)
        self.assertEqual(issue.status, CtrlfIssueStatus.APPROVED)

    def test_should_return_404_on_invalid_issue_id(self):
        # Given: Page와 Issue를 생성한다.
        page, issue, page_history = self._make_page()
        # And: request_body로 유효하지 않은 issue id가 주어진다.
        invalid_issue_id = 2952389
        request_body = {"issue_id": invalid_issue_id}
        # And: owner 정보로 로그인하여 토큰을 발급 받은 상황이다.
        token = self._login(self.owner_data)

        # When: 인증이 필요한 approve issue api를 호출한다.
        response = self._call_api(request_body, token)

        # Then: status code는 404을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And: "이슈 ID를 찾을 수 없습니다."라는 메세지를 리턴한다.
        self.assertEqual(response.data["message"], "이슈 ID를 찾을 수 없습니다.")
        # And: 생성한 Page의 is_approved는 False이다.
        result = PageHistory.objects.get(id=page_history.id)
        self.assertFalse(result.is_approved)
        # And: 생성한 Issue의 Status는 REQUESTD이다
        issue = Issue.objects.get(id=issue.id)
        self.assertEqual(issue.status, CtrlfIssueStatus.REQUESTED)

    def test_should_return_403_on_unauthorized_about_issue(self):
        # Given: Page와 Issue를 생성한다.
        page, issue, page_history = self._make_page()
        # And: request_body로 유효한 issue id가 주어진다.
        request_body = {"issue_id": issue.id}
        # And: owner 정보가 아닌 다른 user 정보로 로그인
        token = self._login(self.user_data)

        # When: 인증이 필요한 approve issue api를 호출한다.
        response = self._call_api(request_body, token)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # And: "승인 권한이 없습니다."라는 메세지를 리턴한다.
        self.assertEqual(response.data["message"], "승인 권한이 없습니다.")
        # And: 생성한 Page의 is_approved는 False이다.
        result = PageHistory.objects.get(id=page_history.id)
        self.assertFalse(result.is_approved)
        # And: 생성한 Issue의 Status는 REQUESTD이다
        issue = Issue.objects.get(id=issue.id)
        self.assertEqual(issue.status, CtrlfIssueStatus.REQUESTED)

    def test_should_update_note_title_on_approving_note_update_issue(self):
        # Given: Note를 생성
        note = Note.objects.create(title="test note title")
        note.owners.add(self.owner)
        # And: issue requester user 생성
        issue_requester_data = {
            "email": "issueRequester@test.com",
            "password": "12345",
        }
        issue_requester = CtrlfUser.objects.create_user(**issue_requester_data)
        # And: issue requester가 note update issue 생성
        issue_data_about_update_note = {
            "owner": issue_requester,
            "title": "new note title",
            "reason": "reason for update note",
            "status": CtrlfIssueStatus.REQUESTED,
            "related_model_type": CtrlfContentType.NOTE,
            "related_model_id": note.id,
            "action": CtrlfActionType.UPDATE,
        }
        issue = Issue.objects.create(**issue_data_about_update_note)
        # And: request body로 issue id가 주어진다.
        request_body = {"issue_id": issue.id}
        # And: note owner 로그인하여 token 발급
        owner_token = self._login(self.owner_data)

        # When: note owner가 issue approve api호출
        response = self._call_api(request_body, owner_token)

        # Then: status code는 200을 리턴
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 기존 Note의 title이 변경된다.
        updated_note = Note.objects.get(id=note.id)
        self.assertEqual(updated_note.title, "new note title")

    def test_should_not_update_note_title_on_issue_approval_user_is_not_note_owner(self):
        # Given: owner가 "owner"뿐인 Note를 생성
        note = Note.objects.create(title="test note title")
        note.owners.add(self.owner)
        # And: issue requester 생성
        issue_requester_data = {
            "email": "issueRequester@test.com",
            "password": "12345",
        }
        issue_requester = CtrlfUser.objects.create_user(**issue_requester_data)
        # And: issue requester가 note update issue 생성
        issue_data_about_update_note = {
            "owner": issue_requester,
            "title": "new note title",
            "reason": "reason for update note",
            "status": CtrlfIssueStatus.REQUESTED,
            "related_model_type": CtrlfContentType.NOTE,
            "related_model_id": note.id,
            "action": CtrlfActionType.UPDATE,
        }
        issue = Issue.objects.create(**issue_data_about_update_note)
        # And: request body로 issue id가 주어진다.
        request_body = {"issue_id": issue.id}
        # And: issue requester 로그인하여 token 발급
        issue_requester_token = self._login(issue_requester_data)

        # When: issue requester가 issue approve api호출
        response = self._call_api(request_body, issue_requester_token)

        # Then: status code는 403을 리턴
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # And: 기존 Note의 title은 그대로이다.
        updated_note = Note.objects.get(id=note.id)
        self.assertEqual(updated_note.title, note.title)

    def test_issue_approve_should_update_topic_title_on_update_issue_approval(self):
        # Given: Topic과 Issue를 생성한다.
        topic_data = {"note": self.note, "title": "test topic title"}
        topic = Topic.objects.create(**topic_data)
        topic.owners.add(self.owner)

        user_info = {
            "email": "test@naver.com",
            "password": "q1w2e3r4",
        }
        issue_request_user = CtrlfUser.objects.create_user(**user_info)
        issue_data = {
            "owner": issue_request_user,
            "title": "new topic title",
            "reason": "reason for topic create",
            "status": CtrlfIssueStatus.REQUESTED,
            "related_model_type": CtrlfContentType.TOPIC,
            "related_model_id": topic.id,
            "action": CtrlfActionType.UPDATE,
        }
        issue = Issue.objects.create(**issue_data)
        # And: request_body로 유효한 issue id가 주어진다.
        request_body = {"issue_id": issue.id}
        # And: owner 정보로 로그인 하여 토큰을 발급받은 상태이다.
        owner_token = self._login(self.owner_data)

        # When: topic owner가 approve issue api를 호출한다.
        response = self._call_api(request_body, owner_token)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: Topic의 title은 변경되어야 한다
        updated_topic = Topic.objects.get(id=topic.id)
        self.assertEqual(updated_topic.title, "new topic title")

    def test_issue_approve_should_not_update_topic_title_on_approval_user_is_not_topic_owner(self):
        # Given: Topic과 Issue를 생성한다.
        topic_data = {"note": self.note, "title": "test topic title"}
        topic = Topic.objects.create(**topic_data)
        topic.owners.add(self.owner)

        user_info = {
            "email": "test@naver.com",
            "password": "q1w2e3r4",
        }
        issue_request_user = CtrlfUser.objects.create_user(**user_info)
        issue_data = {
            "owner": issue_request_user,
            "title": "new topic title",
            "reason": "reason for topic create",
            "status": CtrlfIssueStatus.REQUESTED,
            "related_model_type": CtrlfContentType.TOPIC,
            "related_model_id": topic.id,
            "action": CtrlfActionType.UPDATE,
        }
        issue = Issue.objects.create(**issue_data)
        # And: request_body로 유효한 issue id가 주어진다.
        request_body = {"issue_id": issue.id}
        # And: Issue를 생성한 사람의 token을 만든다
        issue_request_user_token = self._login(user_info)

        # When: topic owner가 아닌, issue를 생성한 유저의 token으로 approve issue api를 호출한다.
        response = self._call_api(request_body, issue_request_user_token)

        # Then: status code는 403을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # And: Topic의 title은 변경되지 않아야 한다.
        updated_topic = Topic.objects.get(id=topic.id)
        self.assertNotEqual(updated_topic.title, "new topic title")

    def test_issue_approve_should_update_page_title_and_content_on_update_issue_approval(self):
        # Given: Page와 Issue를 생성한다.
        page, issue, page_history = self._make_page()
        issue.action = CtrlfActionType.UPDATE
        issue.save()
        # And: page에 대한 page history를 생성한다 - 이미 있던 것
        prev_page_history = PageHistory.objects.get(id=page_history.id)
        # And: page에 대한 page history를 생성한다 - UPDATE
        new_page_history_data = {
            "page": page,
            "owner": self.user,
            "title": "new title",
            "content": "new content",
            "version_type": PageVersionType.UPDATE,
            "version_no": 2,
        }
        new_page_history = PageHistory.objects.create(**new_page_history_data)
        # And: request_body로 유효한 issue id가 주어진다.
        request_body = {"issue_id": issue.id}
        # And: owner 정보로 로그인 하여 토큰을 발급받은 상태이다.
        owner_token = self._login(self.owner_data)

        # When: page owner가 approve issue api를 호출한다.
        response = self._call_api(request_body, owner_token)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 이전 page history의 version type은 PREVIOUS이어야 한다
        prev_page_history = PageHistory.objects.filter(id=prev_page_history.id).first()
        self.assertEqual(prev_page_history.version_type, PageVersionType.PREVIOUS)
        # And: 새로운 page history는 version type이 CURRENT, is_approved=True 이어야한다
        new_page_history = PageHistory.objects.filter(id=new_page_history.id).first()
        self.assertEqual(new_page_history.version_type, PageVersionType.CURRENT)
        self.assertTrue(new_page_history.is_approved)

    def test_issue_approve_should_update_page_title_and_content_on_approval_user_is_not_page_owner(self):
        # Given: Page와 Issue를 생성한다.
        page, issue, page_history = self._make_page()
        issue.action = CtrlfActionType.UPDATE
        # And: issue owner가 page owner와 다른 사람으로 세팅한다
        user_info = {
            "email": "test@naver.com",
            "password": "q1w2e3r4",
        }
        issue_request_user = CtrlfUser.objects.create_user(**user_info)
        issue.owner = issue_request_user
        issue.save()
        # And: page에 대한 page history를 생성한다 - 이미 있던 것
        prev_page_history_data = {
            "page": page,
            "owner": self.user,
            "title": "prev title",
            "content": "prev content",
            "version_type": PageVersionType.CURRENT,
            "version_no": 1,
        }
        PageHistory.objects.create(**prev_page_history_data)
        # And: page에 대한 page history를 생성한다 - UPDATE
        new_page_history_data = {
            "page": page,
            "owner": self.user,
            "title": "new title",
            "content": "new content",
            "version_type": PageVersionType.UPDATE,
            "version_no": 2,
        }
        PageHistory.objects.create(**new_page_history_data)
        # And: request_body로 유효한 issue id가 주어진다.
        request_body = {"issue_id": issue.id}
        # And: page owner가 아닌, issue 요청자의 정보로 토큰을 생성하여서
        issue_request_user_token = self._login(user_info)

        # When: Page owner가 아닌, issue를 생성한 사람이 approve issue api를 호출한다.
        response = self._call_api(request_body, issue_request_user_token)

        # Then: status code는 403을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestIssueCount(IssueTextMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()

    def _call_api(self):
        return self.client.get(reverse("issues:issue_count"))

    def test_issue_count_should_return_count_of_all_issues(self):
        # Given: 5개의 이슈를 생성하고,
        want_to_make_issue_count = 5
        self._make_issues(want_to_make_issue_count)

        # When: api를 호출했을 때,
        response = self._call_api()

        # Then: 생성한 Issue 개수 만큼 리턴 해야한다
        self.assertEqual(response.json()["issues_count"], want_to_make_issue_count)


class TestIssueDelete(IssueTextMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.owner_data = {
            "email": "jinho@naver.com",
            "password": "q1w2e3r4",
        }
        self.owner = CtrlfUser.objects.create_user(**self.owner_data)
        self.note = Note.objects.create(title="basic note")
        self.note.owners.add(self.owner)
        topic_data = {"note": self.note, "title": "basic topic"}
        self.topic = Topic.objects.create(**topic_data)
        self.topic.owners.add(self.owner)

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

    def _call_api(self, request_body, token=None):
        if token:
            header = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        else:
            header = {}
        return self.client.delete(
            reverse("actions:issue_delete"), request_body, content_type="application/json", **header
        )

    def test_issue_delete_on_success_with_page(self):
        # Given: Page와 Issue를 생성한다.
        page, issue, page_history = self._make_page()
        # And: issue의 상태는 Approved가 아니다
        issue.status = CtrlfIssueStatus.REQUESTED
        issue.save()
        # And: request_body로 유효한 issue id가 주어진다.
        request_body = {"issue_id": issue.id}
        # And: owner 정보로 로그인 하여 토큰을 발급받은 상태이다. -> 올바른 권한
        owner_token = self._login(self.owner_data)

        # When: Issue Delete API 를 호출했을 때,
        self._call_api(request_body, owner_token)

        # Then: 이슈는 삭제되어야 한다
        issue = Issue.objects.filter(id=issue.id).first()
        self.assertIsNone(issue)

    def test_issue_delete_on_success_with_topic(self):
        # Given:Topic과 Issue를 생성한다.
        _, issue_id = self._make_topic()
        issue = Issue.objects.get(id=issue_id)
        # And: issue의 상태는 Approved가 아니다
        issue.status = CtrlfIssueStatus.REQUESTED
        issue.save()
        # And: request_body로 유효한 issue id가 주어진다.
        request_body = {"issue_id": issue.id}
        # And: owner 정보로 로그인 하여 토큰을 발급받은 상태이다. -> 올바른 권한
        owner_token = self._login(self.owner_data)

        # When: Issue Delete API 를 호출했을 때,
        self._call_api(request_body, owner_token)

        # Then: 이슈는 삭제되어야 한다
        issue = Issue.objects.filter(id=issue.id).first()
        self.assertIsNone(issue)

    def test_issue_delete_on_success_with_note(self):
        # Given:Note와 Issue를 생성한다.
        _, issue_id = self._make_note()
        issue = Issue.objects.get(id=issue_id)
        # And: issue의 상태는 Approved가 아니다
        issue.status = CtrlfIssueStatus.REQUESTED
        issue.save()
        # And: request_body로 유효한 issue id가 주어진다.
        request_body = {"issue_id": issue.id}
        # And: owner 정보로 로그인 하여 토큰을 발급받은 상태이다. -> 올바른 권한
        owner_token = self._login(self.owner_data)

        # When: Issue Delete API 를 호출했을 때,
        self._call_api(request_body, owner_token)

        # Then: 이슈는 삭제되어야 한다
        issue = Issue.objects.filter(id=issue.id).first()
        self.assertIsNone(issue)

    def test_issue_delete_on_fail_with_bad_request(self):
        # Given:Note와 Issue를 생성한다.
        _, issue_id = self._make_note()
        issue = Issue.objects.get(id=issue_id)
        # And: issue의 상태는 Approved일 때,
        issue.status = CtrlfIssueStatus.APPROVED
        issue.save()
        # And: request_body로 유효한 issue id가 주어진다.
        request_body = {"issue_id": issue.id}
        # And: owner 정보로 로그인 하여 토큰을 발급받은 상태이다. -> 올바른 권한
        owner_token = self._login(self.owner_data)

        # When: Issue Delete API 를 호출했을 때,
        response = self._call_api(request_body, owner_token)

        # Then: 상태코드는 400 이어야 한다
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: 이슈는 삭제 되지 않아야 한다
        issue = Issue.objects.filter(id=issue.id).first()
        self.assertIsNotNone(issue)

    def test_issue_delete_on_fail_with_not_found(self):
        # Given:유효하지 않은 issue_id가 주어지고,
        invalid_issue_id = 9999999
        # And: request_body로 유효하지 않은 issue id가 주어진다.
        request_body = {"issue_id": invalid_issue_id}
        # And: owner 정보로 로그인 하여 토큰을 발급받은 상태이다. -> 올바른 권한
        owner_token = self._login(self.owner_data)

        # When: Issue Delete API 를 호출했을 때,
        response = self._call_api(request_body, owner_token)

        # Then: 상태코드는 404 이어야 한다
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
