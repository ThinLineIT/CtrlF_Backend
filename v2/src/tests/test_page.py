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
    Topic,
)
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status


class TestPageBase(TestCase):
    def setUp(self):
        self.c = Client()
        self.user_data = {"email": "test@test.com", "password": "12345"}
        self.user = CtrlfUser.objects.create_user(**self.user_data)
        self.note = Note.objects.create(title="test note")
        self.note.owners.add(self.user)
        self.topic = Topic.objects.create(note=self.note, title="test topic")
        self.topic.owners.add(self.user)

    def _login(self):
        serializer = LoginSerializer()
        return serializer.validate(self.user_data)["token"]

    def _make_pages_in_topic(self, topic, count):
        page_list = []
        for i in range(count):
            page_data = {"topic": topic, "title": f"test topic{i + 1}", "content": f"test content{i + 1}"}
            page = Page.objects.create(**page_data)
            page.owners.add(self.user)
            page_list.append(page)
        return page_list

    def page_field_test(self, request_body):
        self.page = Page.objects.all()[0]
        owner = self.page.owners.all()[0]
        self.assertEqual(owner, self.user)
        self.assertEqual(self.page.topic.id, request_body["topic_id"])
        self.assertEqual(self.page.title, request_body["title"])
        self.assertEqual(self.page.content, request_body["content"])
        self.assertFalse(self.page.is_approved)

    def page_history_field_test(self, request_body):
        page_history = PageHistory.objects.all()[0]
        self.assertEqual(page_history.owner, self.user)
        self.assertEqual(page_history.page, self.page)
        self.assertEqual(page_history.title, request_body["title"])
        self.assertEqual(page_history.content, request_body["content"])
        self.assertEqual(page_history.version_type, "LATEST")
        self.assertFalse(page_history.is_approved)

    def issue_field_test(self, request_body):
        issue = Issue.objects.all()[0]
        self.assertEqual(issue.owner, self.user)
        self.assertEqual(issue.title, request_body["title"])
        self.assertEqual(issue.reason, request_body["reason"])
        self.assertEqual(issue.status, CtrlfIssueStatus.REQUESTED)
        self.assertEqual(issue.related_model_type, CtrlfContentType.PAGE)
        self.assertEqual(issue.related_model_id, self.page.id)
        self.assertEqual(issue.action, CtrlfActionType.CREATE)


class TestPageList(TestPageBase):
    def _call_api(self, topic_id):
        return self.client.get(reverse("topics:page_list", kwargs={"topic_id": topic_id}))

    def test_page_list_should_return_200(self):
        # Given: 이미 저장된 page들, 유효한 topic id
        topic_id = self.topic.id
        page_list = self._make_pages_in_topic(topic=self.topic, count=10)
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

    def test_page_list_should_return_only_page_list_dependent_on_topic(self):
        # Given: topic A, B를 생성한다.
        topic_A = Topic.objects.create(note=self.note, title="topic A")
        topic_B = Topic.objects.create(note=self.note, title="topic B")
        # And: topic A에 3개, topic B에 5개의 topic을 생성한다.
        self._make_pages_in_topic(topic=topic_A, count=3)
        self._make_pages_in_topic(topic=topic_B, count=5)

        # When: topic A의 id로 page list API 호출한다.
        response = self._call_api(topic_A.id)

        # Then: status code는 200이다,
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: page 개수는 3개이다.
        self.assertEqual(len(response.data), 3)

    def test_page_list_should_return_404_by_invalid_topic_id(self):
        # Given: 이미 저장된 page들, 유효하지 않은 topic id
        invalid_topic_id = 9999
        self._make_pages_in_topic(topic=self.topic, count=10)
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
        page_list = self._make_pages_in_topic(topic=self.topic, count=10)
        # And: 해당 Page에 대한 Issue를 생성하고,
        Issue.objects.create(
            owner=self.user,
            title="page issue",
            reason="page issue content",
            status=CtrlfIssueStatus.APPROVED,
            related_model_type=CtrlfContentType.PAGE,
            related_model_id=page_list[0].id,
            action=CtrlfActionType.CREATE,
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
        self._make_pages_in_topic(topic=self.topic, count=10)
        # And: 해당하는 issue가 없는 상태에서

        # When: API를 실행 했을 때,
        response = self._call_api(valid_topic_id)

        # Then: issue_id가 응답 값 내에 있어야 하고,
        self.assertIn("issue_id", response.data[0])
        # And: page에 해당하는 issue_id는 None 이어야 한다
        self.assertIsNone(response.data[0]["issue_id"])


class TestPageCreate(TestPageBase):
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
            "content": "test page content",
            "topic_id": self.topic.id,
            "reason": "reason for page create",
        }
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받은 상황이다.
        token = self._login()

        # When: 인증이 필요한 create page api를 호출한다.
        response = self._call_api(request_body, token)

        # Then: status code는 201을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # And: Page가 정상적으로 생성된다.
        self.page_field_test(request_body)
        # And: Issue가 정상적으로 생성된다.
        self.issue_field_test(request_body)
        # And: PageHistory가 정상적으로 생성된다.
        self.page_history_field_test(request_body)

    def test_create_page_should_return_400_on_invalid_request_body(self):
        # Given: invalid한 request body가 주어질 때
        invalid_topic_id = 10000
        invalid_request_body = {
            "title": "test title",
            "content": "test page content",
            "topic_id": invalid_topic_id,
            "reason": "reason for page create",
        }
        # And: 로그인 해서 토큰을 발급받은 상황이다.
        token = self._login()

        # When: 인증이 필요한 create page api를 호출한다.
        response = self._call_api(invalid_request_body, token)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Page와 Issue는 생성되지 않는다.
        self.assertEqual(Page.objects.count(), 0)
        self.assertEqual(Issue.objects.count(), 0)

    def test_create_should_return_401_on_unauthorized(self):
        # Given: 로그인 하지 않은 상태에서
        request_body = {
            "title": "test title",
            "content": "test page content",
            "topic_id": self.topic.id,
            "reason": "reason for page create",
        }
        token = None

        # When: 인증이 필요한 create page api를 호출한다.
        response = self._call_api(request_body, token)

        # Then: status code는 401을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # And: Page와 Issue는 생성되지 않는다.
        self.assertEqual(Page.objects.count(), 0)
        self.assertEqual(Issue.objects.count(), 0)


class TestPageDetail(TestPageBase):
    def setUp(self):
        super().setUp()
        self.page = self._make_pages_in_topic(topic=self.topic, count=1)[0]

    def _call_api(self, page_id):
        return self.client.get(reverse("pages:page_detail", kwargs={"page_id": page_id}))

    def test_page_detail_should_return_200(self):
        # Given : 유효한 page id, 이미 저장된 page
        page_id = self.page.id
        # When  : API 실행
        response = self._call_api(page_id)
        # Then  : 상태코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And   : 불러온 정보가 저장된 정보와 일치해야 한다.
        response = response.data
        self.assertEqual(response["title"], self.page.title)
        self.assertEqual(response["content"], self.page.content)
        self.assertEqual(response["topic"], self.topic.id)

    def test_page_detail_should_return_404_by_invalid_page_id(self):
        # Given : 유효하지 않은 page id, 이미 저장된 page
        invalid_page_id = 1234
        # When  : API 실행
        response = self._call_api(invalid_page_id)
        # Then  : 상태코드 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And   : 메세지는 "페이지를 찾을 수 없습니다." 이어야 한다.
        response = response.data
        self.assertEqual(response["message"], "페이지를 찾을 수 없습니다.")
