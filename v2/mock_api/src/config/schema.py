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
        schema_extra = {"example": {"email": "test1234@testcom", "nickname": "유연한외곬",}}


class ErrorSingUp400Response(Schema):
    message: str

    class Config:
        schema_extra = {
            "example": {
                "전달된 값이 유효하지 않을 때,": {"message": "전달된 값이 올바르지 않습니다."},
                "전달된 코드가 일치하지 않을 때, ": {"message": "코드가 일치 하지 않습니다."},
            }
        }
