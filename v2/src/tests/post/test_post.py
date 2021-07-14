# import json

from blog.models import Post
from django.contrib.auth.models import User
from django.test import TestCase

# from django.urls import reverse


class TestPostMixin:
    def setUp(self):
        self.author = self._create_author(username="thkwon", password="test_password")

    @staticmethod
    def _create_post(author, title, text):
        return Post.objects.create(author=author, title=title, text=text)

    @staticmethod
    def _create_author(username, password):
        return User.objects.create_superuser(username=username, password=password)


class Test(TestPostMixin, TestCase):
    def test_temp(self):
        self.assertEqual(1, 1)
