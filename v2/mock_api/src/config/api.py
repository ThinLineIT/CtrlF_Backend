from ninja import NinjaAPI, Router

from config.constants import MOCK_ACCESS_TOKEN, MOCK_REFRESH_TOKEN
from config.schema import (
    SignUpRequestIn,
    ErrorSingUp400Response,
    SignUpRequestOut,
    NickNameDuplicateCheckOut,
    ErrorduplicateNickName404Response,
    ErrorduplicateNickName400Response,
    EmailDuplicateCheckOut,
    ErrorduplicateEmail404Response,
    ErrorduplicateEmail400Response,
    ErrorSendEmail400Response,
    SendEmailAuthIn,
    SendEmailAuthOut,
    LoginRequest,
    ErrorLogin400Response,
    LoginResponse,
    ErrorLogin404Response,
)

api = NinjaAPI(title="CtrlF Mock API Doc")
api_auth = Router(tags=["인증(SignUp, Login, Logout)"])
api.add_router("/auth/", api_auth)


@api_auth.post(
    "/signup",
    summary="회원가입",
    response={200: SignUpRequestOut, 400: ErrorSingUp400Response},
)
def signup(request, request_body: SignUpRequestIn):
    return request_body


@api_auth.get(
    "/signup/nickname/duplicate",
    summary="닉네임 중복검사",
    response={
        200: NickNameDuplicateCheckOut,
        400: ErrorduplicateNickName400Response,
        404: ErrorduplicateNickName404Response,
    },
)
def check_duplicate_nickname(request, data):
    return 200, {"message": "사용 가능한 닉네임입니다."}


@api_auth.get(
    "/signup/email/duplicate",
    summary="이메일 중복 체크",
    response={
        200: EmailDuplicateCheckOut,
        400: ErrorduplicateEmail400Response,
        404: ErrorduplicateEmail404Response,
    },
)
def check_duplicate_email(request, data):
    return 200, {"message": "사용 가능한 이메일 입니다."}


@api_auth.post(
    "/signup/email",
    summary="인증 이메일 보내기",
    response={200: SendEmailAuthOut, 400: ErrorSendEmail400Response},
)
def send_auth_email(request, request_body: SendEmailAuthIn):
    return 200, {"message": "인증 메일이 발송되었습니다."}


@api_auth.post(
    "/login",
    summary="로그인",
    response={
        200: LoginResponse,
        400: ErrorLogin400Response,
        404: ErrorLogin404Response,
    },
)
def login(request, request_body: LoginRequest):
    return 200, {"access_token": MOCK_ACCESS_TOKEN, "refresh_token": MOCK_REFRESH_TOKEN}
