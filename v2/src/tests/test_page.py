import json

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


class PageTestMixin(TestCase):
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
            page = Page.objects.create(topic=topic)
            page.owners.add(self.user)
            page_list.append(page)
        return page_list

    def _make_page_history_in_page(self, page_list, count):
        page_history_list = []
        for i in range(count):
            page_history_data = {
                "title": f"test page title {i + 1}",
                "content": f"test page content {i + 1}",
                "owner": self.user,
                "page": page_list[i],
                "version_type": PageVersionType.CURRENT,
            }
            page_history = PageHistory.objects.create(**page_history_data)
            page_history_list.append(page_history)
        return page_history_list


class TestPageList(PageTestMixin):
    def _call_api(self, topic_id):
        return self.client.get(reverse("topics:page_list", kwargs={"topic_id": topic_id}))

    def _assert_page_list_data_and_expected(self, actual, *expected):
        expected_page_list = expected[0]
        expected_page_history_list = expected[1]
        for i in range(len(actual)):
            data = actual[i]
            expected_page = expected_page_list[i]
            expected_page_history = expected_page_history_list[i]
            self.assertEqual(data["id"], expected_page.id)
            self.assertEqual(data["title"], expected_page_history.title)
            self.assertEqual(data["is_approved"], expected_page_history.is_approved)
            self.assertEqual(data["version_no"], expected_page_history.version_no)
            self.assertEqual(data["topic"], expected_page.topic.id)
            self.assertEqual(data["owners"], [expected_page.owners.first().id])

    def test_page_list_should_return_200_ok_and_page_list(self):
        # Given: Page와 PageHistory 10개 생성, 유효한 topic id가 주어진다.
        valid_topic_id = self.topic.id
        page_list = self._make_pages_in_topic(topic=self.topic, count=10)
        self._make_page_history_in_page(page_list, 10)

        # When : valid topic id로 Page List API 호출한다.
        response = self._call_api(valid_topic_id)

        # Then : status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # And  : 미리 생성한 Page의 개수와 같아야 한다.
        self.assertEqual(len(response.data), len(page_list))

    def test_page_list_should_return_200_ok_by_empty_page_list(self):
        # Given: 유효한 topic id가 주어진다.
        valid_topic_id = self.topic.id

        # When: valid topic id로 Page List API 호출한다.
        response = self._call_api(valid_topic_id)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # And: empty list를 리턴한다.
        self.assertEqual(response.data, [])

    def test_page_list_should_return_only_page_list_belonging_to_specific_topic(self):
        # Given: Topic A, B를 생성한다.
        topic_a = Topic.objects.create(note=self.note, title="topic A")
        topic_b = Topic.objects.create(note=self.note, title="topic B")
        # And: Topic A에 3개, Topic B에 5개의 Page를 생성한다.
        page_list_in_topic_a = self._make_pages_in_topic(topic=topic_a, count=3)
        page_list_in_topic_b = self._make_pages_in_topic(topic=topic_b, count=5)
        # And: 각 Page에 PageHistory를 생성한다.
        self._make_page_history_in_page(page_list_in_topic_a, 3)
        self._make_page_history_in_page(page_list_in_topic_b, 5)

        # When: topic A의 id로 Page List API 호출한다.
        response = self._call_api(topic_a.id)

        # Then: status code는 200이다,
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 리턴된 page의 개수는 3개이다.
        self.assertEqual(len(response.data), len(page_list_in_topic_a))

    def test_page_list_should_return_404_not_found_by_invalid_topic_id(self):
        # Given: Page 10개 생성, 유효하지 않은 topic id가 주어진다.
        invalid_topic_id = 9999
        self._make_pages_in_topic(topic=self.topic, count=10)

        # When: invalid_topic_id로 Page List API 호출한다.
        response = self._call_api(invalid_topic_id)

        # Then: status code는 404이다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And: "토픽을 찾을 수 없습니다."라는 메시지를 리턴한다.
        self.assertEqual(response.data["message"], "토픽을 찾을 수 없습니다.")

    def test_page_list_should_have_necessary_data(self):
        # Given: Page, PageHistory를 10개 생성한다.
        page_list = self._make_pages_in_topic(self.topic, 10)
        page_history_list = self._make_page_history_in_page(page_list, 10)

        # When: valid topic id로 Page List API를 호출한다.
        response = self._call_api(self.topic.id)

        # Then: 응답 데이터에 id, title, topic, owners, version_no, is_approved가 포함되어야한다.
        self._assert_page_list_data_and_expected(response.data, *(page_list, page_history_list))


class TestPageCreate(PageTestMixin):
    def setUp(self):
        super().setUp()
        self.request_body = {
            "title": "test page title",
            "content": "test page content",
            "topic_id": self.topic.id,
            "reason": "some reason",
        }

    def _call_api(self, request_body, token=None):
        if token:
            header = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        else:
            header = {}
        return self.client.post(reverse("pages:page_create"), request_body, **header)

    def _assert_page_model_and_expected(self, request_body):
        self.page = Page.objects.all()[0]
        owner = self.page.owners.all()[0]
        self.assertEqual(owner, self.user)
        self.assertEqual(self.page.topic.id, request_body["topic_id"])

    def _assert_issue_model_and_expected(self, request_body):
        issue = Issue.objects.all()[0]
        self.assertEqual(issue.owner, self.user)
        self.assertEqual(issue.title, request_body["title"])
        self.assertEqual(issue.reason, request_body["reason"])
        self.assertEqual(issue.status, CtrlfIssueStatus.REQUESTED)
        self.assertEqual(issue.related_model_id, self.page_history.id)
        self.assertEqual(issue.related_model_type, CtrlfContentType.PAGE)
        self.assertEqual(issue.action, CtrlfActionType.CREATE)

    def _assert_page_history_model_and_expected(self, request_body):
        self.page_history = PageHistory.objects.all()[0]
        self.assertEqual(self.page_history.owner, self.user)
        self.assertEqual(self.page_history.page, self.page)
        self.assertEqual(self.page_history.title, request_body["title"])
        self.assertEqual(self.page_history.content, request_body["content"])
        self.assertEqual(self.page_history.version_type, "CURRENT")
        self.assertFalse(self.page_history.is_approved)

    def test_create_page_should_return_201_created_and_create_page_and_issue_and_page_history(self):
        # Given: valid한 request body가 주어진다.
        valid_request_body = self.request_body.copy()
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받은 상황이다.
        token = self._login()

        # When: 인증이 필요한 Page Create API를 호출한다.
        response = self._call_api(valid_request_body, token)

        # Then: status code는 201을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # And: Page가 정상적으로 생성된다.
        self._assert_page_model_and_expected(valid_request_body)
        # And: PageHistory가 정상적으로 생성된다.
        self._assert_page_history_model_and_expected(valid_request_body)
        # And: Issue가 정상적으로 생성된다.
        self._assert_issue_model_and_expected(valid_request_body)

    def test_create_page_should_return_400_bad_request_on_invalid_title(self):
        # Given: request body에 invalid title이 주어진다.
        invalid_request_body = self.request_body.copy()
        invalid_request_body["title"] = ""
        # And: 로그인 해서 토큰을 발급받은 상황이다.
        token = self._login()

        # When: 인증이 필요한 Page Create API를 호출한다.
        response = self._call_api(invalid_request_body, token)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Page, PageHistory, Issue는 생성되지 않는다.
        self.assertEqual(Page.objects.count(), 0)
        self.assertEqual(PageHistory.objects.count(), 0)
        self.assertEqual(Issue.objects.count(), 0)

    def test_create_page_should_return_400_bad_request_on_invalid_content(self):
        # Given: request body에 invalid content가 주어진다.
        invalid_request_body = self.request_body.copy()
        invalid_request_body["content"] = ""
        # And: 로그인 해서 토큰을 발급받은 상황이다.
        token = self._login()

        # When: 인증이 필요한 Page Create API를 호출한다.
        response = self._call_api(invalid_request_body, token)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Page, PageHistory, Issue는 생성되지 않는다.
        self.assertEqual(Page.objects.count(), 0)
        self.assertEqual(PageHistory.objects.count(), 0)
        self.assertEqual(Issue.objects.count(), 0)

    def test_create_page_should_return_400_bad_request_on_invalid_topic_id(self):
        # Given: request body에 invalid topic id가 주어진다.
        invalid_request_body = self.request_body.copy()
        invalid_request_body["topic_id"] = 100000
        # And: 로그인 해서 토큰을 발급받은 상황이다.
        token = self._login()

        # When: 인증이 필요한 Page Create API를 호출한다.
        response = self._call_api(invalid_request_body, token)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Page, PageHistory, Issue는 생성되지 않는다.
        self.assertEqual(Page.objects.count(), 0)
        self.assertEqual(PageHistory.objects.count(), 0)
        self.assertEqual(Issue.objects.count(), 0)

    def test_create_page_should_return_400_bad_request_on_invalid_reason(self):
        # Given: request body에 invalid reason가 주어진다.
        invalid_request_body = self.request_body.copy()
        invalid_request_body["reason"] = ""
        # And: 로그인 해서 토큰을 발급받은 상황이다.
        token = self._login()

        # When: 인증이 필요한 Page Create API를 호출한다.
        response = self._call_api(invalid_request_body, token)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Page, PageHistory, Issue는 생성되지 않는다.
        self.assertEqual(Page.objects.count(), 0)
        self.assertEqual(PageHistory.objects.count(), 0)
        self.assertEqual(Issue.objects.count(), 0)

    def test_create_should_return_401_unauthorized_on_not_have_token_in_header(self):
        # Given: valid requset body가 주어진다.
        request_body = self.request_body
        # And: 로그인 하지 않은 상태이다.
        token = None

        # When: 인증이 필요한 Page Create API를 호출한다.
        response = self._call_api(request_body, token)

        # Then: status code는 401을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # And: Page, PageHistory, Issue는 생성되지 않는다.
        self.assertEqual(Page.objects.count(), 0)
        self.assertEqual(PageHistory.objects.count(), 0)
        self.assertEqual(Issue.objects.count(), 0)


class TestPageDetail(PageTestMixin):
    def setUp(self):
        super().setUp()
        self.page_list = self._make_pages_in_topic(topic=self.topic, count=1)
        self.page_history_list = self._make_page_history_in_page(page_list=self.page_list, count=1)

    def _call_api(self, page_id, version_no):
        return self.client.get(reverse("pages:page_detail", kwargs={"page_id": page_id, "version_no": version_no}))

    def _assert_page_detail_data_and_expected(self, data):
        page = self.page_list[0]
        page_history = self.page_history_list[0]
        self.assertEqual(data["id"], page.id)
        self.assertEqual(data["version_no"], page_history.version_no)
        self.assertEqual(data["title"], page_history.title)
        self.assertEqual(data["content"], page_history.content)
        self.assertFalse(data["is_approved"])
        self.assertEqual(data["topic"], self.topic.id)
        self.assertEqual(data["owners"], [self.user.id])

    def test_page_detail_should_return_200_ok_and_page_detail_data(self):
        # Given: 유효한 page id와 version number가 주어진다.
        valid_page_id = self.page_list[0].id
        valid_version_no = 1

        # When: Page Detail API 호출한다.
        response = self._call_api(valid_page_id, valid_version_no)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 필요한 정보들을 리턴한다.
        self._assert_page_detail_data_and_expected(response.data)

    def test_page_detail_should_return_404_not_found_on_invalid_page_id(self):
        # Given: valid version number와 invalid page id가 주어진다.
        invalid_page_id = 1234
        valid_version_no = 1

        # When: Page Detail API 호출한다.
        response = self._call_api(invalid_page_id, valid_version_no)

        # Then: status code는 404를 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And: "페이지를 찾을 수 없습니다." 라는 메시지를 리턴한다.
        self.assertEqual(response.data["message"], "페이지를 찾을 수 없습니다.")

    def test_page_detail_should_return_404_not_found_by_invalid_version_no(self):
        # Given: valid page id와 invalid version number가 주어진다.
        valid_page_id = self.page_list[0].id
        invalid_version_no = 3255

        # When: Page Detail API 호출한다.
        response = self._call_api(valid_page_id, invalid_version_no)

        # Then: status code는 404를 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And: "버전 정보를 찾을 수 없습니다."라는 메시지를 출력한다.
        self.assertEqual(response.data["message"], "버전 정보를 찾을 수 없습니다.")


class TestPageUpdate(PageTestMixin):
    def setUp(self):
        super().setUp()
        self.request_body = {
            "new_title": "new page title",
            "new_content": "new page content",
            "reason": "some reason for page update",
        }

    def _call_api(self, page_id, request_body, token=None):
        if token:
            header = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        else:
            header = {}
        return self.client.put(
            reverse("pages:page_update", kwargs={"page_id": page_id}),
            json.dumps(request_body),
            content_type="application/json",
            **header,
        )

    def _assert_page_history_model_and_expected(self, page, request_body):
        page_history = PageHistory.objects.filter(page=page, version_type=PageVersionType.UPDATE).first()
        self.assertEqual(page_history.owner, self.user)
        self.assertEqual(page_history.page.id, page.id)
        self.assertEqual(page_history.title, request_body["new_title"])
        self.assertEqual(page_history.content, request_body["new_content"])
        self.assertEqual(page_history.version_type, PageVersionType.UPDATE)
        self.assertFalse(page_history.is_approved)

    def _assert_issue_model_and_expected(self, request_body):
        issue = Issue.objects.all()[0]
        self.assertEqual(issue.owner, self.user)
        self.assertEqual(issue.title, request_body["new_title"])
        self.assertEqual(issue.reason, request_body["reason"])
        self.assertEqual(issue.status, CtrlfIssueStatus.REQUESTED)
        self.assertEqual(issue.related_model_type, CtrlfContentType.PAGE)
        self.assertEqual(issue.action, CtrlfActionType.UPDATE)

    def test_update_page_should_return_201_created_and_create_page_history_and_issue(self):
        # Given: valid request body가 주어진다.
        valid_request_body = self.request_body
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받은 상황이다.
        token = self._login()
        # And: page, page history를 1개 생성한다.
        page = self._make_pages_in_topic(self.topic, 1)[0]

        # When : Page Update API를 호출한다.
        response = self._call_api(page_id=page.id, request_body=valid_request_body, token=token)

        # Then : status code는 201을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # And: Page update Issue가 정상적으로 생성된다.
        self._assert_issue_model_and_expected(valid_request_body)
        # And: PageHistory가 정상적으로 생성된다.
        self._assert_page_history_model_and_expected(page, valid_request_body)

    def test_update_page_should_return_404_not_found_on_invalid_page_id(self):
        # Given: valid request body가 주어진다.
        valid_request_body = self.request_body
        # And: 회원가입된 user정보로 로그인을 해서 토큰을 발급받은 상황이다.
        token = self._login()
        # And: invalid page id가 주어진다.
        invalid_page_id = 99999

        # When : invalid page id로 Page Update API를 호출한다.
        response = self._call_api(page_id=invalid_page_id, request_body=valid_request_body, token=token)

        # Then: status code는 404를 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And: "페이지를 찾을 수 없습니다."라는 메세지를 리턴한다.
        self.assertEqual(response.data["message"], "페이지를 찾을 수 없습니다.")
        # And: Issue와 PageHistory는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)
        self.assertEqual(PageHistory.objects.count(), 0)

    def test_update_page_should_return_400_bad_request_on_invalid_new_title(self):
        # Given: request body에 invalid new title이 주어진다.
        invalid_request_body = self.request_body.copy()
        invalid_request_body["new_title"] = ""
        # And: page, page history를 1개를 생성한다.
        page = self._make_pages_in_topic(self.topic, 1)[0]
        # And: 회원가입된 user정보로 로그인해서 토큰을 발급받은 상황이다.
        token = self._login()

        # When: Page Update API를 호출한다.
        response = self._call_api(page_id=page.id, request_body=invalid_request_body, token=token)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: PageHistory와 Issue는 생성되지 않는다.
        page_history_count = PageHistory.objects.filter(version_type=PageVersionType.UPDATE).count()
        self.assertEqual(page_history_count, 0)
        self.assertEqual(Issue.objects.count(), 0)

    def test_update_page_should_return_400_bad_request_on_invalid_new_content(self):
        # Given: request body에 invalid new content가 주어진다.
        invalid_request_body = self.request_body.copy()
        invalid_request_body["new_content"] = ""
        # And: page, page history를 1개를 생성한다.
        page = self._make_pages_in_topic(self.topic, 1)[0]
        # And: 회원가입된 user정보로 로그인해서 토큰을 발급받은 상황이다.
        token = self._login()

        # When: Page Update API를 호출한다.
        response = self._call_api(page_id=page.id, request_body=invalid_request_body, token=token)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: PageHistory와 Issue는 생성되지 않는다.
        page_history_count = PageHistory.objects.filter(version_type=PageVersionType.UPDATE).count()
        self.assertEqual(page_history_count, 0)
        self.assertEqual(Issue.objects.count(), 0)

    def test_update_page_should_return_400_bad_request_on_invalid_reason(self):
        # Given: request body에 invalid reason이 주어진다.
        invalid_request_body = self.request_body.copy()
        invalid_request_body["reason"] = ""
        # And: page, page history를 1개를 생성한다.
        page = self._make_pages_in_topic(self.topic, 1)[0]
        # And: 회원가입된 user정보로 로그인해서 토큰을 발급받은 상황이다.
        token = self._login()

        # When: Page Update API를 호출한다.
        response = self._call_api(page_id=page.id, request_body=invalid_request_body, token=token)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: PageHistory와 Issue는 생성되지 않는다.
        page_history_count = PageHistory.objects.filter(version_type=PageVersionType.UPDATE).count()
        self.assertEqual(page_history_count, 0)
        self.assertEqual(Issue.objects.count(), 0)

    def test_update_page_should_return_401_unauthorized_on_not_have_token_in_header(self):
        # Given: valid requset body가 주어진다.
        request_body = self.request_body
        # And: page, page history를 1개 생성한다.
        page = self._make_pages_in_topic(self.topic, 1)[0]
        # And: 로그인 하지 않은 상태이다.
        token = None

        # When: 인증이 필요한 Page Update API를 호출한다.
        response = self._call_api(page_id=page.id, request_body=request_body, token=token)

        # Then: status code는 401을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # And: PageHistory, Issue는 생성되지 않는다.
        page_history_count = PageHistory.objects.filter(version_type=PageVersionType.UPDATE).count()
        self.assertEqual(page_history_count, 0)
        self.assertEqual(Issue.objects.count(), 0)
