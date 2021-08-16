import json
from unittest.mock import patch

from ctrlf_auth.authentication import CtrlfAuthentication
from ctrlf_auth.helpers import generate_auth_code
from ctrlf_auth.models import CtrlfUser, EmailAuthCode
from ctrlf_auth.serializers import LoginSerializer
from django.test import Client, TestCase
from django.urls import reverse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class TestLogin(TestCase):
    def setUp(self) -> None:
        self.c = Client()
        self.user = CtrlfUser.objects.create_user(email="test123@naver.com", password="12345")

    def _call_api(self):
        return self.c.post(reverse("auth:login"), {"email": "test123@naver.com", "password": "12345"})

    def test_login_should_return_200(self):
        response = self._call_api()
        self.assertEqual(response.status_code, 200)

    def test_login_should_return_token_with_user_id(self):
        response = self._call_api()
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user_id"], self.user.id)


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
    @patch("ctrlf_auth.views.send_email.delay")
    def test_sending_auth_email_should_return_200_on_success(self, mock_send_email_delay, mock_generate_auth_code):
        mock_generate_auth_code.return_value = "1q2w3e4r"
        request_body = {"email": "test1234@test.com"}
        self._call_api(request_body)
        self.assertTrue(EmailAuthCode.objects.filter(code="1q2w3e4r").exists())
        mock_send_email_delay.assert_called_once_with(code="1q2w3e4r", to="test1234@test.com")

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


class TestCheckVerificationCode(TestCase):
    def setUp(self):
        self.c = Client()
        self.code = generate_auth_code()
        EmailAuthCode.objects.create(code=self.code)

    def _call_api(self, request_body):
        return self.c.post(reverse("auth:check_verification_code"), request_body)

    def test_verification_code_should_return_200(self):
        # Given: 일치하는 코드
        request_body = {"code": self.code}
        # When : API 실행
        response = self._call_api(request_body)
        # Then : 상태코드 200 리턴.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And  : 메세지는 "유효한 인증코드 입니다." 이어야 함.
        self.assertEqual(response.data["message"], "유효한 인증코드 입니다.")

    def test_verification_code_should_return_400_by_incorrect_verification_code(self):
        # Given : 불일치하는 코드
        incorrect_code = "incorrect"
        request_body = {"code": incorrect_code}
        # When  : API 실행
        response = self._call_api(request_body)
        # Then  : 상태코드 400 리턴.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And   : 메세지는 "인증코드가 올바르지 않습니다." 이어야 함.
        self.assertEqual(response.data["message"], "인증코드가 올바르지 않습니다.")

    def test_verification_code_should_return_400_by_incorrect_length_code(self):
        # Given : 인증코드 최대길이를 넘어가는 코드
        incorrect_code = "incorrect_length_code"
        request_body = {"code": incorrect_code}
        # When  : API 실행
        response = self._call_api(request_body)
        # Then  : 상태코드 400 리턴.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # And   : 메세지는 "인증코드가 올바르지 않습니다." 이어야 함.
        self.assertEqual(response.data["message"], "인증코드가 올바르지 않습니다.")


class MockAuthAPI(APIView):
    authentication_classes = [CtrlfAuthentication]

    @swagger_auto_schema(deprecated=True, tags=["기타"])
    def get(self, request):
        return Response(status=status.HTTP_200_OK, data={"email": request.user.email})


class TestJWTAuth(TestCase):
    def setUp(self):
        self.c = Client()

    def _call_mock_api(self, token=None):
        if token:
            header = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        else:
            header = {}
        return self.c.get(reverse("auth:mock_auth_api"), **header)

    def test_jwt_auth_on_success(self):
        # Given: kwon5604@naver.com email로 이미 가입이 되어 있고,
        data = {
            "email": "kwon5604@naver.com",
            "password": "1234",
        }
        user = CtrlfUser.objects.create_user(**data)
        # And: login 하여서 token을 발급 받은 상황 일 때,
        serializer = LoginSerializer()
        serialized = serializer.validate(data)

        # When: 인증이 필수인 mock api를 호출 했을 때,
        response = self._call_mock_api(token=serialized["token"])

        # Then: 200을 리턴해야한다
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 토큰 payload에 일치하는 ctrlf user instance를 리턴해야한
        self.assertEqual(json.loads(response.content)["email"], user.email)

    def test_jwt_auth_should_return_401_unauthorized_on_not_including_auth_header(self):
        # When: 로그인이 되지 않은 상황(토큰없음) 인증이 필수인 mock api를 호출 했을 때,
        response = self._call_mock_api()

        # Then: 401을 리턴해야한다
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # And: 인증이 유효하지 않습니다. 메세지를 리턴해야한다
        self.assertEqual(json.loads(response.content)["message"], "인증이 유효하지 않습니다.")

    def test_jwt_auth_should_return_401_unauthorized_on_token_is_invalid(self):
        # When: 유효하지 않은 토큰으로 인증이 필수인 mock api를 호출 했을 때,
        response = self._call_mock_api(token="invalid_token")

        # Then: 401을 리턴해야한다
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # And: 인증이 유효하지 않습니다. 메세지를 리턴해야한다
        self.assertEqual(json.loads(response.content)["message"], "인증이 유효하지 않습니다.")
