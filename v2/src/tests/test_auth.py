from unittest.mock import patch

from ctrlf_auth.helpers import generate_auth_code
from ctrlf_auth.models import CtrlfUser, EmailAuthCode
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

    @patch("ctrlf_auth.views.generate_auth_code")
    @patch("ctrlf_auth.views.EmailAuthCode.send_email")
    def test_sending_auth_email_should_return_200_on_success(self, mock_send_email, mock_generate_auth_code):
        mock_generate_auth_code.return_value = "1q2w3e4r"
        request_body = {"email": "test1234@test.com"}
        response = self._call_api(request_body)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(EmailAuthCode.objects.filter(code="1q2w3e4r").exists())
        mock_send_email.assert_called_once_with(to="test1234@test.com")

    def test_sending_auth_email_should_return_400_on_email_from_request_body_is_invalid_format(self):
        request_body = {"email": "test1234test.com"}  # invalid email format
        response = self._call_api(request_body)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "유효하지 않은 이메일 형식 입니다.")


class TestGenerateAuthCode(TestCase):
    def test_generate_auth_code(self):
        code = generate_auth_code()
        self.assertEqual(len(code), 8)
        self.assertRegexpMatches(code, "[a-zA-Z0-9]")
