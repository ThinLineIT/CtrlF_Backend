import json

from blog.models import Post
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status


class TestPostMixin:
    def setUp(self):
        self.author = self._create_author(username="thkwon", password="test_password")

    @staticmethod
    def _create_post(author, title, text):
        return Post.objects.create(author=author, title=title, text=text)

    @staticmethod
    def _create_author(username, password):
        return User.objects.create_superuser(username=username, password=password)


class TestPostDetail(TestPostMixin, TestCase):
    def setUp(self):
        super().setUp()

    def test_post_detail(self):
        # Given: post가 생성되었을 때
        post = self._create_post(author=self.author, title="test title", text="test text")
        post.publish()

        # When: 생성된 post의 id를 인자로 담아 api를 실행
        response = self.client.get(reverse("post_detail_update_delete", kwargs={"post_id": 1}))

        # Then: 상태코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # And: 생성된 post의 정보와 일치.
        response_data = json.loads(response.content)["post"]
        self.assertEqual(response_data["author"], self.author.id)
        self.assertEqual(response_data["title"], "test title")
        self.assertEqual(response_data["text"], "test text")

    def test_post_detail_on_error_with_404_not_found(self):
        # Given: post가 없을 때 (잘못된 post id)
        # When: 생성된 post의 id를 인자로 담아 api를 실행
        response = self.client.get(reverse("post_detail_update_delete", kwargs={"post_id": 1}))

        # Then: 상태코드 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # And: "Post를 찾을 수 없습니다" 메세지 리턴.
        response_data = json.loads(response.content)["message"]
        self.assertEqual(response_data, "Post를 찾을 수 없습니다")
