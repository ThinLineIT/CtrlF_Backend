from ctrlf_auth.models import CtrlfUser
from django.test import Client, TestCase
from django.urls import reverse


class TestLogin(TestCase):
    def test_login_should_return_200(self):
        CtrlfUser.objects.create_user(email="test123@naver.com", password="12345")
        c = Client()
        response = c.post(reverse("auth:login"), {"email": "test123@naver.com", "password": "12345"})
        self.assertEqual(response.status_code, 200)
