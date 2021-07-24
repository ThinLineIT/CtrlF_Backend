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


class TestSignUp(TestCase):
    def setUp(self) -> None:
        self.c = Client()

    def _call_api(self, request_body):
        return self.c.post(reverse("auth:signup"), request_body)

    def test_signup_should_return_201_on_success(self):
        valid_request_body = {
            "email": "test1234@test.com",
            "code": "YWJjZGU=",
            "nickname": "유연한외곬",
            "password": "testpassword%*",
            "password_confirm": "testpassword%*",
        }
        response = self._call_api(valid_request_body)
        self.assertEqual(response.status_code, 201)

    def test_signup_should_return_message_on_success(self):
        valid_request_body = {
            "email": "test1234@test.com",
            "code": "YWJjZGU=",
            "nickname": "유연한외곬",
            "password": "testpassword%*",
            "password_confirm": "testpassword%*",
        }
        response = self._call_api(valid_request_body)
        self.assertEqual(response.data["message"], "환영합니다.\n가입이 완료되었습니다\n\n로그인 후 이용해주세요.")

    def test_signup_should_return_400_on_fail_with_duplicated_email(self):
        user_data = {"email": "test1234@test.com", "password": "testpassword%*"}  # email이 이미 중복 됨
        CtrlfUser.objects.create_user(**user_data)
        user_data.update({"code": "YWJjZGU=", "nickname": "유연한외곬", "password_confirm": "testpassword%*"})
        response = self._call_api(user_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "중복된 email 입니다.")

    def test_signup_should_return_400_on_fail_with_no_same_password(self):
        user_data = {
            "email": "test1234@test.com",
            "code": "YWJjZGU=",
            "nickname": "유연한외곬",
            "password": "no_same_password",
            "password_confirm": "testpassword%*",
        }
        response = self._call_api(user_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "패스워드가 일치하지 않습니다.")


class TestSendingAuthEmail(TestCase):
    def setUp(self) -> None:
        self.c = Client()

    def _call_api(self, request_body):
        return self.c.post(reverse("auth:sending_auth_email"), request_body)

    def test_sending_auth_email_should_return_200_on_success(self):
        request_body = {
            "email": "test1234@test.com",
        }
        response = self._call_api(request_body)
        self.assertEqual(response.status_code, 200)
