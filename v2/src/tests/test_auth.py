from unittest.mock import patch

from ctrlf_auth.helpers import generate_auth_code
from ctrlf_auth.models import CtrlfUser, EmailAuthCode
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


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
        EmailAuthCode.objects.create(code="YWJjZGU=")

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

    def test_signup_should_return_400_on_fail_with_invalid_code(self):
        user_data = {
            "email": "test1234@test.com",
            "code": "invalid_code",  # invalid code
            "nickname": "유연한외곬",
            "password": "testpassword%*",
            "password_confirm": "testpassword%*",
        }
        response = self._call_api(user_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "유효하지 않은 코드 입니다.")


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


class TestNicknameDuplicate(TestCase):
    def setUp(self) -> None:
        self.c = Client()

    def _call_api(self, nickname):
        return self.c.get(reverse("auth:check_nickname_duplicate"), {"data": nickname})

    def test_check_nickname_duplicate_should_return_200_on_success(self):
        # Given: 유효한 닉네임이 주어진다.
        valid_nickname = "nickname"

        # When: check nickname duplicate api를 호출한다.
        response = self._call_api(valid_nickname)

        # Then: status code 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: "사용 가능한 닉네임입니다."라는 메시지를 리턴한다.
        self.assertEqual(response.data["message"], "사용 가능한 닉네임입니다.")

    def test_check_nickname_duplicate_should_return_400_on_duplicate_nickname(self):
        # Given: "test_nickname"이라는 닉네임을 가진 user와, 중복된 닉네임이 주어진다.
        CtrlfUser.objects.create(email="test123@naver.com", password="12345", nickname="nickname")
        duplicate_nickname = "nickname"

        # When: check nickname duplicate api를 호출한다.
        response = self._call_api(duplicate_nickname)

        # Then: status code 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And: "이미 존재하는 닉네임입니다."라는 메시지를 리턴한다.
        self.assertEqual(response.data["message"], "이미 존재하는 닉네임입니다.")

    def test_check_nickname_duplicate_should_return_400_on_containing_white_space(self):
        # Given: 공백이 포함된 닉네임이 주어진다.
        invalid_nickname = "nick name"

        # When: check nickname duplicate api를 호출한다.
        response = self._call_api(invalid_nickname)

        # Then: status code 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And : "전달 된 값이 올바르지 않습니다.\n영어,숫자,한글2~10자\n특수문자x\n공백x"라는 메시지를 리턴한다.
        self.assertEqual(response.data["message"], "전달 된 값이 올바르지 않습니다.\n영어,숫자,한글2~10자\n특수문자x\n공백x")

    def test_check_nickname_duplicate_should_return_400_on_containing_special_character(self):
        # Given: 특수문자가 포함된 닉네임이 주어진다.
        invalid_nickname = "nickname!!"

        # When: check nickname duplicate api를 호출한다.
        response = self._call_api(invalid_nickname)

        # Then: status code 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And : "전달 된 값이 올바르지 않습니다.\n영어,숫자,한글2~10자\n특수문자x\n공백x"라는 메시지를 리턴한다.
        self.assertEqual(response.data["message"], "전달 된 값이 올바르지 않습니다.\n영어,숫자,한글2~10자\n특수문자x\n공백x")

    def test_check_nickname_duplicate_should_return_400_on_length_less_than_2(self):
        # Given: 길이가 2보다 작은 닉네임이 주어진다.
        invalid_nickname = "K"

        # When: check nickname duplicate api를 호출한다.
        response = self._call_api(invalid_nickname)

        # Then: status code 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And : "전달 된 값이 올바르지 않습니다.\n영어,숫자,한글2~10자\n특수문자x\n공백x"라는 메시지를 리턴한다.
        self.assertEqual(response.data["message"], "전달 된 값이 올바르지 않습니다.\n영어,숫자,한글2~10자\n특수문자x\n공백x")

    def test_check_nickname_duplicate_should_return_400_on_length_more_than_10(self):
        # Given: 길이가 10보다 큰 닉네임이 주어진다.
        invalid_nickname = "미안하다이거보여주려고어그로끌었다"

        # When: check nickname duplicate api를 호출한다.
        response = self._call_api(invalid_nickname)

        # Then: status code 400을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And : "전달 된 값이 올바르지 않습니다.\n영어,숫자,한글2~10자\n특수문자x\n공백x"라는 메시지를 리턴한다.
        self.assertEqual(response.data["message"], "전달 된 값이 올바르지 않습니다.\n영어,숫자,한글2~10자\n특수문자x\n공백x")


class TestCheckEmailDuplicate(TestCase):
    def setUp(self):
        self.c = Client()

    def _call_api(self, email):
        return self.c.get(reverse("auth:check_email_duplicate"), {"data": email})

    def test_check_email_duplicate_should_return_200(self):
        # Given : 중복되지 않고 유효한 이메일
        email = "sehwa@test.com"
        # When  : API 실행
        response = self._call_api(email)
        # Then  : 상태코드 200 리턴.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And   : 메세지는 "사용 가능한 이메일 입니다." 이어야 함.
        self.assertEqual(response.data["message"], "사용 가능한 이메일 입니다.")

    def test_check_email_duplicate_should_return_400_by_invalid_email_pattern(self):
        # Given : 유효하지 않은 형식의 이메일
        invalid_email = "sehwatestcom"
        # When  : API 실행
        response = self._call_api(invalid_email)
        # Then  : 상태코드 400 리턴.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And   : 메세지는 "이메일 형식이 유효하지 않습니다." 이어야 함.
        self.assertEqual(response.data["message"], "이메일 형식이 유효하지 않습니다.")

    def test_check_email_duplicate_should_return_404_by_duplicated_email(self):
        # Given : 중복된 이메일
        existed_email = "exist@test.com"
        CtrlfUser.objects.create_user(email=existed_email, password="test1234")
        # When  : API 실행.
        response = self._call_api(existed_email)
        # Then  : 상태코드 404 리턴.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # And   : 메세지는 "이미 존재하는 이메일 입니다." 이어야 함.
        self.assertEqual(response.data["message"], "이미 존재하는 이메일 입니다.")


class MockAuthAPI(APIView):
    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class TestJWTAuth(TestCase):
    def setUp(self):
        self.c = Client()

    def _call_mock_api(self):
        return self.c.get(reverse("auth:mock_auth_api"))

    def test_jwt_auth_on_success(self):
        # When: 인증이 필수인 mock api를 호출 했을 때,
        response = self._call_mock_api()
        # Then: 200을 리턴해야한다
        self.assertEqual(response.status_code, status.HTTP_200_OK)
