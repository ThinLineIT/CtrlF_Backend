import json

from ctrlf_auth.models import CtrlfUser
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
from ctrlfbe.serializers import IssueCreateSerializer
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from .test_mixin import _get_header, _login


class PageTestMixin:
    def setUp(self):
        self.client = Client()
        self.user_data = {"email": "test@test.com", "password": "12345"}
        self.user = CtrlfUser.objects.create_user(**self.user_data)
        self.note = Note.objects.create(title="test note title")
        self.note.owners.add(self.user)
        self.topic = Topic.objects.create(note=self.note, title="test topic title")
        self.topic.owners.add(self.user)

    def _call_page_list_api(self, topic_id):
        return self.client.get(reverse("topics:page_list", kwargs={"topic_id": topic_id}))

    def _call_page_create_api(self, request_body, token=None):
        return self.client.post(reverse("pages:page_create"), request_body, **_get_header(token))

    def _call_page_detail_api(self, page_id, version_no):
        return self.client.get(
            reverse("pages:page_detail_update_delete", kwargs={"page_id": page_id}), {"version_no": version_no}
        )

    def _call_page_update_api(self, request_body, page_id, token=None):
        return self.client.put(
            reverse("pages:page_detail_update_delete", kwargs={"page_id": page_id}),
            json.dumps(request_body),
            content_type="application/json",
            **_get_header(token),
        )

    def _call_page_delete_api(self, request_body, page_id, token=None):
        return self.client.delete(
            reverse("pages:page_detail_update_delete", kwargs={"page_id": page_id}),
            json.dumps(request_body),
            content_type="application/json",
            **_get_header(token),
        )

    def _call_issue_approve_api(self, issue_id, token):
        return self.client.post(reverse("actions:issue_approve"), {"issue_id": issue_id}, **_get_header(token))

    def _make_pages_in_topic(self, topic, count):
        page_list = []
        for _ in range(count):
            page = Page.objects.create(topic=topic)
            page.owners.add(self.user)
            page_list.append(page)
        return page_list

    def _make_page_history_in_page(self, page_list):
        page_history_list = []
        for i in range(len(page_list)):
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


class TestPageList(PageTestMixin, TestCase):
    def _assert_page_list_and_expected(self, actual, expected):
        page_list = expected[0]
        page_history_list = expected[1]
        for i in range(len(actual)):
            self.assertEqual(actual[i]["id"], page_list[i].id)
            self.assertEqual(actual[i]["title"], page_history_list[i].title)
            self.assertEqual(actual[i]["is_approved"], page_history_list[i].is_approved)
            self.assertEqual(actual[i]["version_no"], page_history_list[i].version_no)
            self.assertEqual(actual[i]["topic"], page_list[i].topic.id)
            self.assertIn(page_history_list[i].owner.id, actual[i]["owners"])

    def test_page_list_should_return_200_ok_and_page_list(self):
        # Given: Topic에 Page를 10개 생성한다.
        page_list = self._make_pages_in_topic(topic=self.topic, count=10)
        # And: 각 Page에 PageHistory를 생성한다.
        page_history_list = self._make_page_history_in_page(page_list)
        # And: Topic id가 주어진다.
        valid_topic_id = self.topic.id

        # When: Page List API를 호출한다.
        response = self._call_page_list_api(valid_topic_id)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 응답 데이터의 Page의 개수는 미리 생성한 Page의 개수와 같다.
        self.assertEqual(len(response.data), len(page_list))
        # And: 응답 데이터의 Page list에 필요한 정보들이 포함되어야 한다.
        self._assert_page_list_and_expected(actual=response.data, expected=(page_list, page_history_list))

    def test_page_list_should_return_200_ok_on_empty_page_list(self):
        # Given: Page, PageHistory 생성없이 유효한 Topic id가 주어진다.
        valid_topic_id = self.topic.id

        # When: Page List API 호출한다.
        response = self._call_page_list_api(valid_topic_id)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: empty list를 리턴한다.
        self.assertEqual(response.data, [])

    def test_page_list_should_return_page_list_only_belonging_to_specific_topic(self):
        # Given: Topic A, B를 생성한다.
        topic_a = Topic.objects.create(note=self.note, title="topic A")
        topic_b = Topic.objects.create(note=self.note, title="topic B")
        # And: Topic A에 3개, Topic B에 5개의 Page를 생성한다.
        page_list_in_topic_a = self._make_pages_in_topic(topic=topic_a, count=3)
        page_list_in_topic_b = self._make_pages_in_topic(topic=topic_b, count=5)
        # And: 각 Page에 PageHistory를 생성한다.
        page_history_list_in_topic_a = self._make_page_history_in_page(page_list_in_topic_a)
        self._make_page_history_in_page(page_list_in_topic_b)
        # And: Topic A의 id가 주어진다.
        valid_topic_id = topic_a.id

        # When: Page List API 호출한다.
        response = self._call_page_list_api(valid_topic_id)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 리턴된 Page의 개수는 Topic A에 생성된 Page의 개수와 같다
        self.assertEqual(len(response.data), len(page_list_in_topic_a))
        # And: 응답 데이터의 Page list에 필요한 정보들이 포함되어야 한다.
        self._assert_page_list_and_expected(
            actual=response.data, expected=(page_list_in_topic_a, page_history_list_in_topic_a)
        )

    def test_page_list_should_return_404_not_found_by_invalid_topic_id(self):
        # Given: Page 10개 생성한다. 유효하지 않은 topic id가 주어진다.
        page_list = self._make_pages_in_topic(topic=self.topic, count=10)
        # And: 각 Page에 PageHistory를 생성한다.
        self._make_page_history_in_page(page_list)
        # And: 유효하지 않은 Topic id가 주어진다.
        invalid_topic_id = 9999

        # When: Page List API 호출한다.
        response = self._call_page_list_api(invalid_topic_id)

        # Then: status code는 404를 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And: "토픽을 찾을 수 없습니다."라는 메시지를 리턴한다.
        self.assertEqual(response.data["message"], "토픽을 찾을 수 없습니다.")


class TestPageCreate(PageTestMixin, TestCase):
    def _create_page_and_page_history_and_issue_by_calling_topic_create_api(self):
        page_create_request_body = {
            "title": "test page title",
            "content": "test page content",
            "topic_id": self.topic.id,
            "reason": "some reason for page create",
        }
        user_token_of_creating_new_page = _login(self.user_data)
        self._call_page_create_api(page_create_request_body, user_token_of_creating_new_page)

    def _assert_page_and_expected(self, actual, expected):
        self.assertEqual(actual.topic.id, expected["topic_id"])
        self.assertIn(self.user, actual.owners.all())

    def _assert_issue_about_page_create_and_expected(self, actual, expected):
        self.assertEqual(actual.title, expected["title"])
        self.assertEqual(actual.reason, expected["reason"])
        self.assertEqual(actual.owner.id, self.user.id)
        self.assertEqual(actual.status, CtrlfIssueStatus.REQUESTED)
        self.assertEqual(actual.related_model_type, CtrlfContentType.PAGE)
        self.assertEqual(actual.related_model_id, PageHistory.objects.first().id)
        self.assertEqual(actual.action, CtrlfActionType.CREATE)
        self.assertEqual(actual.etc, expected["title"])

    def _assert_page_history_and_expected(self, actual, expected):
        self.assertEqual(actual.owner, self.user)
        self.assertEqual(actual.page, Page.objects.first())
        self.assertEqual(actual.title, expected["title"])
        self.assertEqual(actual.content, expected["content"])
        self.assertEqual(actual.version_type, PageVersionType.CURRENT)
        self.assertEqual(actual.version_no, 1)
        self.assertFalse(actual.is_approved)

    def test_create_page_should_return_201_created_and_create_page_and_issue_and_page_history(self):
        # Given: PageHistory title, content와 Topic id, Issue reason이 주어진다.
        valid_request_body = {
            "title": "test page title",
            "content": "test page content",
            "topic_id": self.topic.id,
            "reason": "some reason for page create",
        }
        # And: 로그인 해서 토큰을 발급받는다.
        user_token_of_creating_new_page = _login(self.user_data)

        # When: 인증이 필요한 Page Create API를 호출한다.
        response = self._call_page_create_api(valid_request_body, user_token_of_creating_new_page)

        # Then: status code는 201을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # And: Page가 정상적으로 생성된다.
        self._assert_page_and_expected(actual=Page.objects.first(), expected=valid_request_body)
        # And: PageHistory가 정상적으로 생성된다.
        self._assert_page_history_and_expected(actual=PageHistory.objects.first(), expected=valid_request_body)
        # And: Issue가 정상적으로 생성된다.
        self._assert_issue_about_page_create_and_expected(actual=Issue.objects.first(), expected=valid_request_body)

    def test_create_page_should_return_404_not_found_on_invalid_topic_id(self):
        # Given: 유효하지 않은 Topic id가 주어진다.
        invalid_topic_id = 6889465
        invalid_request_body = {
            "title": "test page title",
            "content": "test page content",
            "topic_id": invalid_topic_id,
            "reason": "some reason for page create",
        }
        # And: 로그인 해서 토큰을 발급받는다.
        token = _login(self.user_data)

        # When: 인증이 필요한 Page Create API를 호출한다.
        response = self._call_page_create_api(invalid_request_body, token)

        # Then: status code는 404을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And: Page는 생성되지 않는다.
        self.assertEqual(Page.objects.count(), 0)
        # And: PageHistory는 생성되지 않는다.
        self.assertEqual(PageHistory.objects.count(), 0)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_create_page_should_return_400_bad_request_on_invalid_title(self):
        # Given: 유효하지 않은 PageHistory title이 주어진다.
        invalid_title = ""
        invalid_request_body = {
            "title": invalid_title,
            "content": "test page content",
            "topic_id": self.topic.id,
            "reason": "some reason for page create",
        }
        # And: 로그인 해서 토큰을 발급받는다.
        user_token_of_creating_new_page = _login(self.user_data)

        # When: 인증이 필요한 Page Create API를 호출한다.
        response = self._call_page_create_api(invalid_request_body, user_token_of_creating_new_page)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Page는 생성되지 않는다.
        self.assertEqual(Page.objects.count(), 0)
        # And: PageHistory는 생성되지 않는다.
        self.assertEqual(PageHistory.objects.count(), 0)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_create_page_should_return_400_bad_request_on_invalid_content(self):
        # Given: 유효하지 않은 PageHistory content가 주어진다.
        invalid_content = ""
        invalid_request_body = {
            "title": "test page title",
            "content": invalid_content,
            "topic_id": self.topic.id,
            "reason": "some reason for page create",
        }
        # And: 로그인 해서 토큰을 발급받는다.
        user_token_of_creating_new_page = _login(self.user_data)

        # When: 인증이 필요한 Page Create API를 호출한다.
        response = self._call_page_create_api(invalid_request_body, user_token_of_creating_new_page)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Page는 생성되지 않는다.
        self.assertEqual(Page.objects.count(), 0)
        # And: PageHistory는 생성되지 않는다.
        self.assertEqual(PageHistory.objects.count(), 0)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_create_page_should_return_400_bad_request_on_invalid_reason(self):
        # Given: 유효하지 않은 Issue reason이 주어진다.
        invalid_reason = ""
        invalid_request_body = {
            "title": "test page title",
            "content": "test page content",
            "topic_id": self.topic.id,
            "reason": invalid_reason,
        }
        # And: 로그인 해서 토큰을 발급받은 상황이다.
        user_token_of_creating_new_page = _login(self.user_data)

        # When: 인증이 필요한 Page Create API를 호출한다.
        response = self._call_page_create_api(invalid_request_body, user_token_of_creating_new_page)

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Page는 생성되지 않는다.
        self.assertEqual(Page.objects.count(), 0)
        # And: PageHistory는 생성되지 않는다.
        self.assertEqual(PageHistory.objects.count(), 0)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_create_should_return_401_unauthorized_on_not_have_token_in_header(self):
        # Given: PageHistory title, content와 Topic id, Issue reason이 주어진다.
        invalid_request_body = {
            "title": "test page title",
            "content": "test page content",
            "topic_id": self.topic.id,
            "reason": "some reason for page create",
        }
        # And: 로그인은 하지 않는다.
        invalid_token = None

        # When: 인증이 필요한 Page Create API를 호출한다.
        response = self._call_page_create_api(invalid_request_body, invalid_token)

        # Then: status code는 401을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # And: Page는 생성되지 않는다.
        self.assertEqual(Page.objects.count(), 0)
        # And: PageHistory는 생성되지 않는다.
        self.assertEqual(PageHistory.objects.count(), 0)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)

    def test_should_change_field_of_is_approved_to_true_on_approving_issue_about_page_create(self):
        # Given: Page Create API를 호출하여 Page, 미승인 상태의 PageHistory, Page Create Issue를 생성한다.
        self._create_page_and_page_history_and_issue_by_calling_topic_create_api()
        # And: Page Create Issue의 id가 주어진다.
        page_create_issue_id = Issue.objects.first().id
        # And: 해당 Issue에 권한을 가진 token을 발급 받는다.
        user_token_of_having_permission_to_issue_approve = _login(self.user_data)

        # When: Page Create Issue에 대한 Issue Approve API를 호출한다.
        response = self._call_issue_approve_api(page_create_issue_id, user_token_of_having_permission_to_issue_approve)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: PageHistory의 is_approved가 True가 된다.
        page_history = PageHistory.objects.first()
        self.assertTrue(page_history.is_approved)

    def test_should_not_change_field_of_is_approved_to_true_on_not_having_permission_to_issue_about_page_create(self):
        # Given: Page Create API를 호출하여 Page, 미승인 상태의 PageHistory, Page Create Issue를 생성한다.
        self._create_page_and_page_history_and_issue_by_calling_topic_create_api()
        # And: Page Create Issue의 id가 주어진다.
        page_create_issue_id = Issue.objects.first().id
        # And: 해당 Issue에 권한이 없는 token을 발급 받는다.
        another_user_data = {"email": "test2@test.com", "password": "12345"}
        CtrlfUser.objects.create_user(**another_user_data)
        user_token_of_not_having_permission_to_issue_approve = _login(another_user_data)

        # When: Page Create Issue에 대한 Issue Approve API를 호출한다.
        response = self._call_issue_approve_api(
            page_create_issue_id, user_token_of_not_having_permission_to_issue_approve
        )

        # Then: status code는 403을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # And: Page의 is_approved는 그대로 False이다.
        page_history = PageHistory.objects.first()
        self.assertFalse(page_history.is_approved)


class TestPageDetail(PageTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.page = self._make_pages_in_topic(topic=self.topic, count=1)[0]
        self.page_history = self._make_page_history_in_page(page_list=[self.page])[0]

    def _assert_page_detail_and_expected(self, actual, expected):
        page = expected[0]
        page_history = expected[1]
        self.assertEqual(actual["id"], page.id)
        self.assertEqual(actual["version_no"], page_history.version_no)
        self.assertEqual(actual["title"], page_history.title)
        self.assertEqual(actual["content"], page_history.content)
        self.assertEqual(actual["is_approved"], page_history.is_approved)
        self.assertEqual(actual["topic"], page.topic.id)
        self.assertIn(page.owners.first().id, actual["owners"])

    def test_page_detail_should_return_200_ok_and_page_detail_data(self):
        # Given: 유효한 Page id가 주어진다.
        valid_page_id = self.page.id
        # And: 유효한 PageHistory version_no가 주어진다.
        valid_version_no = self.page_history.version_no

        # When: Page Detail API를 호출한다.
        response = self._call_page_detail_api(valid_page_id, valid_version_no)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 응답 데이터에 필요한 정보들을 리턴한다.
        page = Page.objects.get(id=valid_page_id)
        page_history = PageHistory.objects.get(version_no=valid_version_no)
        self._assert_page_detail_and_expected(actual=response.data, expected=(page, page_history))

    def test_page_detail_should_return_404_not_found_on_invalid_page_id(self):
        # Given: 유효하지 않은 Page id가 주어진다.
        invalid_page_id = 1234
        # And: 유효한 PageHistory version_no가 주어진다.
        valid_version_no = 1

        # When: Page Detail API 호출한다.
        response = self._call_page_detail_api(invalid_page_id, valid_version_no)

        # Then: status code는 404를 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And: "페이지를 찾을 수 없습니다." 라는 메시지를 리턴한다.
        self.assertEqual(response.data["message"], "페이지를 찾을 수 없습니다.")

    def test_page_detail_should_return_404_not_found_by_invalid_version_no(self):
        # Given: 유효한 Page id가 주어진다.
        valid_page_id = self.page.id
        # And: 유효하지 않은 PageHistory version_no가 주어진다.
        invalid_version_no = 3255

        # When: Page Detail API 호출한다.
        response = self._call_page_detail_api(valid_page_id, invalid_version_no)

        # Then: status code는 404를 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And: "버전 정보를 찾을 수 없습니다."라는 메시지를 출력한다.
        self.assertEqual(response.data["message"], "버전 정보를 찾을 수 없습니다.")


class TestPageUpdate(PageTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.page = self._make_pages_in_topic(self.topic, 1)[0]
        self.page_history = self._make_page_history_in_page([self.page])[0]

    def _create_issue_about_page_update_and_page_history_by_calling_page_update_api(self):
        page_update_request_body = {
            "new_title": "new page title",
            "new_content": "new page content",
            "reason": "some reason for page update",
        }
        user_token_of_creating_update_page_issue = _login(self.user_data)
        valid_page_id = self.page.id
        self._call_page_update_api(page_update_request_body, valid_page_id, user_token_of_creating_update_page_issue)

    def _assert_page_history_and_expected(self, actual, expected):
        self.assertEqual(actual.owner, self.user)
        self.assertEqual(actual.page.id, self.page.id)
        self.assertEqual(actual.title, expected["new_title"])
        self.assertEqual(actual.content, expected["new_content"])
        self.assertEqual(actual.version_type, PageVersionType.UPDATE)
        self.assertEqual(actual.version_no, 2)
        self.assertFalse(actual.is_approved)

    def _assert_issue_about_page_update_and_expected(self, actual, expected):
        self.assertEqual(actual.owner, self.user)
        self.assertEqual(actual.title, expected["new_title"])
        self.assertEqual(actual.reason, expected["reason"])
        self.assertEqual(actual.status, CtrlfIssueStatus.REQUESTED)
        self.assertEqual(actual.related_model_type, CtrlfContentType.PAGE)
        self.assertEqual(actual.related_model_id, 2)
        self.assertEqual(actual.action, CtrlfActionType.UPDATE)

    def test_page_update_should_return_201_created_and_create_page_history_and_issue(self):
        # Given: 새로운 title, content와 Issue reason이 주어진다.
        valid_request_body = {
            "new_title": "new page title",
            "new_content": "new page content",
            "reason": "some reason for page update",
        }
        # And: 로그인 해서 토큰을 발급받는다.
        user_token_of_creating_page_update_issue = _login(self.user_data)
        # And: 수정할 Page id가 주어진다.
        valid_page_id = self.page.id

        # When: 인증이 필요한 Page Update API를 호출한다.
        response = self._call_page_update_api(
            valid_request_body, valid_page_id, user_token_of_creating_page_update_issue
        )

        # Then : status code는 201을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # And: Page update Issue가 정상적으로 생성된다.
        issue = Issue.objects.first()
        self._assert_issue_about_page_update_and_expected(actual=issue, expected=valid_request_body)
        # And: PageHistory가 정상적으로 생성된다.
        page_history = PageHistory.objects.filter(version_type=PageVersionType.UPDATE).first()
        self._assert_page_history_and_expected(actual=page_history, expected=valid_request_body)

    def test_page_update_should_return_404_not_found_on_invalid_page_id(self):
        # Given: 새로운 title, content와 Issue reason이 주어진다.
        valid_request_body = {
            "new_title": "new page title",
            "new_content": "new page content",
            "reason": "some reason for page update",
        }
        # And: 로그인 해서 토큰을 발급받는다.
        user_token_of_creating_page_update_issue = _login(self.user_data)
        # And: 유효하지 않은 Page id가 주어진다.
        invalid_page_id = 99999

        # When: 인증이 필요한 Page Update API를 호출한다.
        response = self._call_page_update_api(
            valid_request_body, invalid_page_id, user_token_of_creating_page_update_issue
        )

        # Then: status code는 404를 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And: "페이지를 찾을 수 없습니다."라는 메세지를 리턴한다.
        self.assertEqual(response.data["message"], "페이지를 찾을 수 없습니다.")
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)
        # And: PageHistory는 생성되지 않는다.
        new_page_history = PageHistory.objects.filter(version_type=PageVersionType.UPDATE)
        self.assertEqual(new_page_history.count(), 0)

    def test_page_update_should_return_400_bad_request_on_invalid_new_title(self):
        # Given: 유효하지 않은 새 title이 주어진다.
        invalid_new_title = ""
        invalid_request_body = {
            "new_title": invalid_new_title,
            "new_content": "new page content",
            "reason": "some reason for page update",
        }
        # And: 로그인 해서 토큰을 발급받는다.
        user_token_of_creating_page_update_issue = _login(self.user_data)
        # And: 수정할 Page id가 주어진다.
        valid_page_id = self.page.id

        # When: 인증이 필요한 Page Update API를 호출한다.
        response = self._call_page_update_api(
            invalid_request_body, valid_page_id, user_token_of_creating_page_update_issue
        )

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)
        # And: PageHistory는 생성되지 않는다.
        new_page_history = PageHistory.objects.filter(version_type=PageVersionType.UPDATE)
        self.assertEqual(new_page_history.count(), 0)

    def test_page_update_should_return_400_bad_request_on_invalid_new_content(self):
        # Given: 유효하지 않은 새 content가 주어진다.
        invalid_new_content = ""
        invalid_request_body = {
            "new_title": "new page title",
            "new_content": invalid_new_content,
            "reason": "some reason for page update",
        }
        # And: 로그인 해서 토큰을 발급받는다.
        user_token_of_creating_page_update_issue = _login(self.user_data)
        # And: 수정할 Page id가 주어진다.
        valid_page_id = self.page.id

        # When: 인증이 필요한 Page Update API를 호출한다.
        response = self._call_page_update_api(
            invalid_request_body, valid_page_id, user_token_of_creating_page_update_issue
        )

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)
        # And: PageHistory는 생성되지 않는다.
        new_page_history = PageHistory.objects.filter(version_type=PageVersionType.UPDATE)
        self.assertEqual(new_page_history.count(), 0)

    def test_page_update_should_return_400_bad_request_on_invalid_reason(self):
        # Given: 유효하지 않은 Issue reason이 주어진다.
        invalid_reason = ""
        invalid_request_body = {
            "new_title": "new page title",
            "new_content": "new page content",
            "reason": invalid_reason,
        }
        # And: 로그인 해서 토큰을 발급받는다.
        user_token_of_creating_page_update_issue = _login(self.user_data)
        # And: 수정할 Page id가 주어진다.
        valid_page_id = self.page.id

        # When: 인증이 필요한 Page Update API를 호출한다.
        response = self._call_page_update_api(
            invalid_request_body, valid_page_id, user_token_of_creating_page_update_issue
        )

        # Then: status code는 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)
        # And: PageHistory는 생성되지 않는다.
        new_page_history = PageHistory.objects.filter(version_type=PageVersionType.UPDATE)
        self.assertEqual(new_page_history.count(), 0)

    def test_page_update_should_return_401_unauthorized_on_not_have_token_in_header(self):
        # Given: 새로운 title, content와 Issue reason이 주어진다.
        valid_request_body = {
            "new_title": "new page title",
            "new_content": "new page content",
            "reason": "some reason for page update",
        }
        # And: 로그인은 하지 않는다.
        invalid_token = None
        # And: 수정할 Page id가 주어진다.
        valid_page_id = self.page.id

        # When: 인증이 필요한 Page Update API를 호출한다.
        response = self._call_page_update_api(valid_request_body, valid_page_id, invalid_token)

        # Then: status code는 401을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # And: Issue는 생성되지 않는다.
        self.assertEqual(Issue.objects.count(), 0)
        # And: PageHistory는 생성되지 않는다.
        new_page_history = PageHistory.objects.filter(version_type=PageVersionType.UPDATE)
        self.assertEqual(new_page_history.count(), 0)

    def test_should_change_version_type_to_previous_on_approving_issue_about_page_update(self):
        # Given: Page Update API를 호출하여 Topic Update Issue와 새 PageHistory를 생성한다.
        self._create_issue_about_page_update_and_page_history_by_calling_page_update_api()
        # And: Page Update Issue가 주어진다.
        valid_issue = Issue.objects.first()
        # And: 해당 Issue에 권한이 있는 user token을 발급받는다.
        user_token_of_having_permission_to_issue_approve = _login(self.user_data)

        # When: Page Update Issue에 대한 Issue Approve API를 호출한다.
        response = self._call_issue_approve_api(valid_issue.id, user_token_of_having_permission_to_issue_approve)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 기존의 PageHistory의 PageVersionType은 PREVIOUS이다.
        original_page_history = PageHistory.objects.get(version_no=1)
        self.assertEqual(original_page_history.version_type, PageVersionType.PREVIOUS)
        # And: Issue Approve에 대한 PageHistory의 PageVersionType은 CURRENT이다.
        new_page_history = PageHistory.objects.get(version_no=2)
        self.assertEqual(new_page_history.version_type, PageVersionType.CURRENT)

    def test_should_not_change_version_type_to_previous_on_not_having_permission_to_topic_update_issue(self):
        # Given: Page Update API를 호출하여 Topic Update Issue와 새 PageHistory를 생성한다.
        self._create_issue_about_page_update_and_page_history_by_calling_page_update_api()
        # And: Page Update Issue가 주어진다.
        valid_issue = Issue.objects.first()
        # And: 해당 Issue에 권한이 없는 user token을 발급받는다.
        another_user_data = {"email": "test2@test.com", "password": "12345"}
        CtrlfUser.objects.create_user(**another_user_data)
        user_token_not_having_permission_to_issue = _login(another_user_data)

        # When: Page Update Issue에 대한 Issue Approve API를 호출한다.
        response = self._call_issue_approve_api(valid_issue.id, user_token_not_having_permission_to_issue)

        # Then: status code는 403을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # And: 기존의 PageHistory의 PageVersionType은 그대로 CURRENT이다.
        original_page_history = PageHistory.objects.get(version_no=1)
        self.assertEqual(original_page_history.version_type, PageVersionType.CURRENT)
        # And: Issue Approve에 대한 PageHistory의 PageVersionType은 UPDATE이다.
        new_page_history = PageHistory.objects.get(version_no=2)
        self.assertEqual(new_page_history.version_type, PageVersionType.UPDATE)


class TestPageDelete(PageTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.page = self._make_pages_in_topic(self.topic, 1)[0]
        self.page_history = self._make_page_history_in_page([self.page])[0]

    def test_page_delete_on_success(self):
        # Given: 새로운 Page title과 Issue reason이 주어진다.
        valid_request_body = {
            "reason": "reason for delete page",
        }
        # And: 로그인 해서 토큰을 발급받는다.
        user_token_of_creating_page_delete_issue = _login(self.user_data)
        # And: 수정할 Page id가 주어진다.
        valid_note_id = self.topic.id

        # When: Page 삭제 API를 호출 했을 떄
        self._call_page_delete_api(valid_request_body, valid_note_id, user_token_of_creating_page_delete_issue)

        # Then: Issue가 정상적으로 생성된다.
        issue = Issue.objects.first()
        self.assertEqual(issue.title, f"{self.page_history.title} 삭제")
        self.assertEqual(issue.reason, valid_request_body["reason"])
        self.assertEqual(issue.owner.id, self.user.id)
        self.assertEqual(issue.status, CtrlfIssueStatus.REQUESTED)
        self.assertEqual(issue.related_model_type, CtrlfContentType.PAGE)
        self.assertEqual(issue.related_model_id, self.page_history.id)
        self.assertEqual(issue.action, CtrlfActionType.DELETE)

    def test_page_delete_on_fail_with_invalid_topic_id(self):
        # Given: 새로운 Page title과 Issue reason이 주어진다.
        valid_request_body = {
            "reason": "reason for delete page",
        }
        # And: 로그인 해서 토큰을 발급받는다.
        user_token_of_creating_page_delete_issue = _login(self.user_data)
        # And: 유효하지 않은 수정할 Page id가 주어진다.
        invalid_topic_id = 9999999

        # When: Page 삭제 API를 호출 했을 떄
        response = self._call_page_delete_api(
            valid_request_body, invalid_topic_id, user_token_of_creating_page_delete_issue
        )

        # Then: status code는 404을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And: "페이지를 찾을 수 없습니다."라는 메시지를 리턴한다.
        self.assertEqual(response.data["message"], "페이지를 찾을 수 없습니다.")
        # Then: Issue가 생성되지 않아야 한다
        issue = Issue.objects.first()
        self.assertIsNone(issue)

    def test_should_delete_note_on_approving_issue_about_page_delete(self):
        # Given: Page Delete Issue를 생성한다
        page_delete_request_body = {"reason": "reason for page delete"}
        issue_data = {
            "owner": self.user.id,
            "title": f"{self.page_history.title} 삭제",
            "related_model_type": CtrlfContentType.PAGE,
            "action": CtrlfActionType.DELETE,
            "status": CtrlfIssueStatus.REQUESTED,
            "reason": page_delete_request_body["reason"],
        }
        issue_serializer = IssueCreateSerializer(data=issue_data)
        issue_serializer.is_valid(raise_exception=True)
        issue_serializer.save(related_model=self.note)
        # And: Page Delete Issue가 주어진다.
        valid_issue = Issue.objects.first()
        # And: 해당 Issue에 권한이 있는 user token을 발급받는다.
        issue_approve_user_token = _login(self.user_data)

        # When: Page Delete Issue에 대한 Issue Approve API를 호출한다.
        response = self._call_issue_approve_api(valid_issue.id, issue_approve_user_token)

        # Then: status code는 204이다.
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # And: issue도 삭제되어야 한다
        valid_issue = Issue.objects.first()
        self.assertIsNone(valid_issue)
        # And: Page는 None 이어야 한다
        self.assertIsNone(Page.objects.filter(id=self.page.id).first())

    def test_should_not_delete_topic_on_not_having_permission_about_delete_topic_issue(self):
        # Given: Page Delete Issue를 생성한다
        page_delete_request_body = {"reason": "reason for page delete"}
        issue_data = {
            "owner": self.user.id,
            "title": f"{self.page_history.title} 삭제",
            "related_model_type": CtrlfContentType.PAGE,
            "action": CtrlfActionType.DELETE,
            "status": CtrlfIssueStatus.REQUESTED,
            "reason": page_delete_request_body["reason"],
        }
        issue_serializer = IssueCreateSerializer(data=issue_data)
        issue_serializer.is_valid(raise_exception=True)
        issue_serializer.save(related_model=self.note)
        # And: Page Delete Issue가 주어진다.
        valid_issue = Issue.objects.first()
        # And: 해당 Issue에 권한이 없는 user의 토큰을 발급받는다.
        another_user_data = {"email": "test2@test.com", "password": "12345"}
        CtrlfUser.objects.create_user(**another_user_data)
        user_token_not_having_permission_to_issue = _login(another_user_data)

        # When: Page Delete Issue에 대한 Issue Approve API를 호출한다.
        response = self._call_issue_approve_api(valid_issue.id, user_token_not_having_permission_to_issue)

        # Then: status code는 403이다.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # And: Page는 삭제되지 않아야 한다.
        self.assertIsNotNone(Page.objects.filter(id=self.page.id).first())
