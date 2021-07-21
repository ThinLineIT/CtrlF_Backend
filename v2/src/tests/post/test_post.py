import json

from blog.models import Post
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.status import HTTP_200_OK


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
        # Given: 10개의 publish한 post를 생성한다.
        for i in range(10):
            post = self._create_post(author=self.author, title=f"test title-{i}", text=f"test text-{i}")
            post.publish()

        # When: retrieve post list api 호출
        response = self.client.get(reverse("retrieve_post_list"))

        # Then: 상태코드는 200이다.
        self.assertEqual(response.status_code, HTTP_200_OK)
        # And: 10개의 post 데이터를 리턴한다.
        response_data = json.loads(response.content)["posts"]
        self.assertEqual(len(response_data), 10)

    def test_list_with_published_post(self):
        # Given: publish한 post를 1개 생성한다.
        post = self._create_post(author=self.author, title="test title", text="test text")
        post.publish()

        # When: retrieve post list api 호출
        response = self.client.get(reverse("retrieve_post_list"))

        # Then: 상태코드는 200이다.
        self.assertEqual(response.status_code, HTTP_200_OK)
        # And: posts의 개수는 1개이며 post의 정보를 가지고있다.
        response_data = json.loads(response.content)["posts"]
        self.assertEqual(response_data[0]["title"], "test title")
        self.assertEqual(response_data[0]["text"], "test text")
        self.assertEqual(response_data[0]["author"], self.author.username)

    def test_list_with_no_published_post(self):
        # Given: publish하지 않은 1개의 post를 생성한다.
        self._create_post(author=self.author, title="test title", text="test text")

        # When: retrieve post list api 호출
        response = self.client.get(reverse("retrieve_post_list"))

        # Then: 상태코드는 200이다.
        self.assertEqual(response.status_code, HTTP_200_OK)
        # And: publish를 하지 않았기 때문에 posts의 개수는 0개이다.
        response_data = json.loads(response.content)["posts"]
        self.assertEqual(len(response_data), 0)
