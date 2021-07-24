from ctrlf_auth.models import CtrlfUser
from django.test import Client, TestCase
from django.urls import reverse


class TestLogin(TestCase):
    def setUp(self) -> None:
        self.c = Client()
        CtrlfUser.objects.create_user(email="test123@naver.com", password="12345")

    def _call_api(self):
        return self.c.post(reverse("auth:login"), {"email": "test123@naver.com", "password": "12345"})

    def test_login_should_return_200(self):
        response = self._call_api()
        self.assertEqual(response.status_code, 200)

    def test_login_should_return_token(self):
        response = self._call_api()
        self.assertIn("token", response.data)
