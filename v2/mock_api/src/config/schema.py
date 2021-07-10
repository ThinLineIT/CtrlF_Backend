from ninja import Schema


class SignUpRequestIn(Schema):
    email: str
    code: str
    nickname: str
    password: str
    password_confirm: str

    class Config:
        schema_extra = {
            "example": {
                "email": "test1234@testcom",
                "code": "YWJjZGU=",
                "nickname": "유연한외곬",
                "password": "testpassword%*",
                "password_confirm": "testpassword%*",
            }
        }


class SignUpRequestOut(Schema):
    email: str
    nickname: str

    class Config:
        schema_extra = {"example": {"email": "test1234@testcom", "nickname": "유연한외곬"}}


class ErrorSignUp400Response(Schema):
    message: str

    class Config:
        schema_extra = {
            "example": {
                "전달된 값이 유효하지 않을 때,": {"message": "전달된 값이 올바르지 않습니다."},
                "전달된 코드가 일치하지 않을 때, ": {"message": "코드가 일치 하지 않습니다."},
            }
        }


class ErrorduplicateNickName400Response(Schema):
    message: str

    class Config:
        schema_extra = {"example": {"전달된 값이 유효하지 않을 때,": {"message": "전달된 값이 올바르지 않습니다."}}}


class ErrorduplicateNickName404Response(Schema):
    message: str

    class Config:
        schema_extra = {"example": {"닉네임 중복": {"message": "이미 존재하는 닉네임입니다."}}}


class NickNameDuplicateCheckOut(Schema):
    message: str

    class Config:
        schema_extra = {"example": {"message": "사용 가능한 닉네임입니다."}}


class ErrorduplicateEmail400Response(Schema):
    message: str

    class Config:
        schema_extra = {"example": {"이메일 형식 유효하지 않음": {"message": "이메일 형식이 유효하지 않습니다."}}}


class ErrorduplicateEmail404Response(Schema):
    message: str

    class Config:
        schema_extra = {"example": {"이메일 중복": {"message": "이미 존재하는 이메일 입니다."}}}


class EmailDuplicateCheckOut(Schema):
    message: str

    class Config:
        schema_extra = {"example": {"message": "사용 가능한 이메일 입니다."}}


class ErrorSendEmail400Response(Schema):
    message: str

    class Config:
        schema_extra = {"example": {"이메일 형식 유효하지 않음": {"message": "이메일 형식이 유효하지 않습니다."}}}


class SendEmailAuthIn(Schema):
    email: str

    class Config:
        schema_extra = {"example": {"email": "test1234@test.com"}}


class SendEmailAuthOut(Schema):
    message: str

    class Config:
        schema_extra = {"example": {"email": "test1234@test.com"}}


class LoginRequest(Schema):
    email: str
    password: str

    class Config:
        schema_extra = {"example": {"email": "test1234@test.com", "password": "password123!"}}


class LoginResponse(Schema):
    access_token: str
    refresh_token: str


class ErrorLogin400Response(Schema):
    message: str

    class Config:
        schema_extra = {
            "example": {
                "이메일 형식 유효하지 않음": {"message": "이메일 형식이 유효하지 않습니다."},
                "패스워드 불 일치": {"message": "패스워드가 유효하지 않습니다."},
            }
        }


class ErrorLogin404Response(Schema):
    message: str

    class Config:
        schema_extra = {"example": {"이메일이 존재하지 않음": {"message": "이메일이 존재하지 않습니다."}}}


class LogoutRequest(Schema):
    email: str

    class Config:
        schema_extra = {"example": {"email": "test1234@test.com"}}


class LogoutResponse(Schema):
    message: str

    class Config:
        schema_extra = {"example": {"message": "로그아웃 되었습니다."}}


class ErrorLogout400Response(Schema):
    message: str

    class Config:
        schema_extra = {"example": {"이메일 형식 유효하지 않음": {"message": "이메일 형식이 유효하지 않습니다."}}}


class ErrorLogout404Response(Schema):
    message: str

    class Config:
        schema_extra = {"example": {"이메일이 존재하지 않음": {"message": "이메일이 존재하지 않습니다."}}}
