import json

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
