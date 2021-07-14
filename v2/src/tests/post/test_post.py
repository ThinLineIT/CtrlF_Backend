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


class TestPostCreate(TestPostMixin, TestCase):
    def setUp(self):
        super().setUp()

    def test_post_create(self):
        # Given: 유효한 request body 값이 주어질 때,
        request_body = {"author": self.author.id, "title": "test title", "text": "test text"}

        # When: post 생성 api를 호출하면,
        response = self.client.post(reverse("post_list_create"), data=request_body)

        # Then: 상태코드는 201 이고, Post의 개수는 1개이다
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.all().count(), 1)
        # And: 응답 값에서 생성된 post의 title과 text를 리턴한다
        response = json.loads(response.content)["post"]
        self.assertEqual(response["title"], "test title")
        self.assertEqual(response["text"], "test text")

    def test_post_create_with_error_on_404(self):
        # Given: 유효하지 않은 author_id가 주어질 때,
        invalid_author_id = 123123123
        request_body = {"author": invalid_author_id, "title": "test title", "text": "test text"}

        # When: post 생성 api를 호출하면,
        response = self.client.post(reverse("post_list_create"), data=request_body)

        # Then: 상태코드는 404이고, Post의 개수는 0개이다.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Post.objects.all().count(), 0)
        # And: 응답 값으로 "author를 찾을 수 없습니다."를 리턴한다
        response = json.loads(response.content)
        self.assertEqual(response["message"], "author를 찾을 수 없습니다.")

    def test_post_create_without_title(self):
        # Given: title이 없을 때
        request_body = {"author": self.author.id, "title": "", "text": "test text"}

        # When: post 생성 api 호출
        response = self.client.post(reverse("post_list_create"), data=request_body)

        # then: 상태코드 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # And: 응답 값으로 "title이 없습니다." 리턴.
        response = json.loads(response.content)
        self.assertEqual(response["message"], "title이 없습니다.")

    def test_post_create_without_text(self):
        # Given: text가 없을 때
        request_body = {"author": self.author.id, "title": "text title", "text": ""}

        # When: post 생성 api 호출
        response = self.client.post(reverse("post_list_create"), data=request_body)

        # then: 상태코드 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # And: 응답 값으로 "text가 없습니다." 리턴.
        response = json.loads(response.content)
        self.assertEqual(response["message"], "text가 없습니다.")
