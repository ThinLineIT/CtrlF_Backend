import json
from http.client import NOT_FOUND, OK, BAD_REQUEST

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Post


class TestPostMixin:
    def setUp(self):
        self.author = self._create_author(username="thkwon", password="test_password")

    @staticmethod
    def _create_post(author, title, text):
        return Post.objects.create(author=author, title=title, text=text)

    @staticmethod
    def _create_author(username, password):
        return User.objects.create_superuser(username=username, password=password)


class TestPostList(TestPostMixin, TestCase):
    def setUp(self):
        super().setUp()

    def test_list_with_count(self):
        for i in range(10):
            post = self._create_post(
                author=self.author, title=f"test title-{i}", text=f"test text-{i}"
            )
            post.publish()
        response = self.client.get(reverse("retrieve_post_list"))
        response_data = json.loads(response.content)["posts"]
        self.assertEqual(len(response_data), 10)

    def test_list_with_published_post(self):
        post = self._create_post(
            author=self.author, title="test title", text="test text"
        )
        post.publish()
        response = self.client.get(reverse("retrieve_post_list"))
        response_data = json.loads(response.content)["posts"]
        self.assertEqual(response_data[0]["title"], "test title")
        self.assertEqual(response_data[0]["text"], "test text")
        self.assertEqual(response_data[0]["author"], self.author.id)

    def test_list_with_no_published_post(self):
        self._create_post(author=self.author, title="test title", text="test text")
        response = self.client.get(reverse("retrieve_post_list"))
        response_data = json.loads(response.content)["posts"]
        self.assertEqual(len(response_data), 0)


class TestPostDetail(TestPostMixin, TestCase):
    def setUp(self):
        super().setUp()

    def test_post_detail(self):
        post = self._create_post(
            author=self.author, title="test title", text="test text"
        )
        post.publish()
        response = self.client.get(reverse("retrieve_post_detail", kwargs={"id": 1}))
        response_data = json.loads(response.content)["post"]
        self.assertEqual(response.status_code, OK)
        self.assertEqual(response_data["author"], self.author.id)
        self.assertEqual(response_data["title"], "test title")
        self.assertEqual(response_data["text"], "test text")

    def test_post_detail_on_error_with_404_not_found(self):
        response = self.client.get(reverse("retrieve_post_detail", kwargs={"id": 1}))
        response_data = json.loads(response.content)["message"]
        self.assertEqual(response.status_code, NOT_FOUND)
        self.assertEqual(response_data, "Post를 찾을 수 없습니다")


class TestPostCreate(TestPostMixin, TestCase):
    def setUp(self):
        super().setUp()

    def test_post_create(self):
        # Given: 유효한 request body 값이 주어질 때,
        request_body = {
            "author": self.author.id,
            "title": "test title",
            "text": "test text",
        }

        # When: post 생성 api를 호출하면,
        response = self.client.post(reverse("create_post"), data=request_body)

        # Then: 상태코드는 201 이고, Post의 개수는 1개이다
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Post.objects.all().count(), 1)
        # And: 응답 값에서 생성된 post의 title과 text를 리턴한다
        response = json.loads(response.content)["post"]
        self.assertEqual(response["title"], "test title")
        self.assertEqual(response["text"], "test text")

    def test_post_create_with_error_on_404(self):
        # Given: 유효하지 않은 author_id가 주어질 때,
        invalid_author_id = 123123123
        request_body = {
            "author": invalid_author_id,
            "title": "test title",
            "text": "test text",
        }

        # When: post 생성 api를 호출하면,
        response = self.client.post(reverse("create_post"), data=request_body)

        # Then: 상태코드는 404이고, Post의 개수는 0개이다.
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Post.objects.all().count(), 0)
        # And: 응답 값으로 "author를 찾을 수 없습니다."를 리턴한다
        response = json.loads(response.content)
        self.assertEqual(response["message"], "author를 찾을 수 없습니다.")


class TestPostUpdate(TestPostMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(
            author=self.author, title="test title", text="test text"
        )

    def test_post_update_with_put(self):
        # Given: 업데이트 하기 위한 유효한 request body 값이 주어지고,
        request_body_for_put_update = json.dumps(
            {
                "author": self.author.id,
                "title": "test test title",
                "text": "test test text",
            }
        )

        # When: 1번 post에 대한 업데이트 api를 호출 할 때,
        response = self.client.put(
            reverse("update_post_with_put", kwargs={"id": self.post.id}),
            data=request_body_for_put_update,
        )

        # Then: 상태코드는 200이고,
        self.assertEqual(response.status_code, 200)
        # And: 실제 post는 변경되어야 한다
        post = Post.objects.all()[0]
        self.assertEqual(post.author.id, self.author.id)
        self.assertEqual(post.title, "test test title")
        self.assertEqual(post.text, "test test text")
        # And: 응답 값에서도 변경된 것을 확인할 수 있다
        response = json.loads(response.content)["post"]
        self.assertEqual(response["title"], "test test title")
        self.assertEqual(response["text"], "test test text")

    def test_post_update_with_error_with_author_on_404(self):
        # Given: 업데이트 하기 위한 유효하지 않은 author_id 값이 주어지고,
        invalid_author_id = 123123123
        request_body_for_put_update = json.dumps(
            {
                "author": invalid_author_id,
                "title": "test test title",
                "text": "test test text",
            }
        )

        # When: 1번 post에 대한 업데이트 api를 호출 할 때,
        response = self.client.put(
            reverse("update_post_with_put", kwargs={"id": self.post.id}),
            data=request_body_for_put_update,
        )

        # Then: 상태코드는 404이고,
        self.assertEqual(response.status_code, 404)
        # And: 실제 post는 변경 되지 않아야 한다
        post = Post.objects.all()[0]
        self.assertEqual(post.author.id, self.author.id)
        self.assertEqual(post.title, "test title")
        self.assertEqual(post.text, "test text")
        # And: 응답 메세지로 author를 찾을 수 없습니다. 를 리턴 해야 한다.
        response = json.loads(response.content)
        self.assertEqual(response["message"], "author를 찾을 수 없습니다.")

    def test_post_update_with_error_with_post_on_404(self):
        # Given: 업데이트 하기 위한 유효하지 않은 post_id 값이 주어지고,
        request_body_for_put_update = json.dumps(
            {
                "author": self.author.id,
                "title": "test test title",
                "text": "test test text",
            }
        )
        invalid_post_id = 12345

        # When: # When: 유효하지 않은 post에 대한 업데이트 api를 호출 할 때,
        response = self.client.put(
            reverse("update_post_with_put", kwargs={"id": invalid_post_id}),
            data=request_body_for_put_update,
        )

        # Then: 상태코드는 404이고,
        self.assertEqual(response.status_code, 404)
        # And: 실제 post는 변경 되지 않아야 한다
        post = Post.objects.all()[0]
        self.assertEqual(post.author.id, self.author.id)
        self.assertEqual(post.title, "test title")
        self.assertEqual(post.text, "test text")
        response = json.loads(response.content)
        # And: 응답 메세지로 post를 찾을 수 없습니다. 를 리턴 해야 한다.
        self.assertEqual(response["message"], "post를 찾을 수 없습니다.")

    def test_post_update_with_error_with_post_on_400(self):
        # Given: 업데이트 하기 위한 유효하지 않은 request body 값이 주어지고,
        # And: 그 이외 post_id와 author_id가 정상적으로 주어질 때
        request_body_for_put_update = json.dumps(
            {"author": self.author.id, "title": None, "text": None}
        )

        # When: 1번 post에 대한 업데이트 api를 호출 할 때,
        response = self.client.put(
            reverse("update_post_with_put", kwargs={"id": self.post.id}),
            data=request_body_for_put_update,
        )

        # Then: 상태코드는 400이고,
        self.assertEqual(response.status_code, BAD_REQUEST)
        # And: 실제 post는 변경 되지 않아야 한다
        post = Post.objects.all()[0]
        self.assertEqual(post.author.id, self.author.id)
        self.assertEqual(post.title, "test title")
        self.assertEqual(post.text, "test text")
        # And: 응답 메세지로 올바르지 않은 요청입니다. 를 리턴 해야 한다.
        response = json.loads(response.content)
        self.assertEqual(response["message"], "올바르지 않은 요청입니다.")
