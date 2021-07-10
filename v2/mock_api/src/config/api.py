from ninja import NinjaAPI, Router

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
)

api = NinjaAPI()
api_auth = Router()
api.add_router("/auth/", api_auth)


@api_auth.post("/signup", response={200: SignUpRequestOut, 400: ErrorSingUp400Response})
def signup(request, request_body: SignUpRequestIn):
    return request_body


@api_auth.get(
    "/signup/nickname/duplicate",
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
    response={
        200: EmailDuplicateCheckOut,
        400: ErrorduplicateEmail400Response,
        404: ErrorduplicateEmail404Response,
    },
)
def check_duplicate_email(request, data):
    return 200, {"message": "사용 가능한 이메일 입니다."}
