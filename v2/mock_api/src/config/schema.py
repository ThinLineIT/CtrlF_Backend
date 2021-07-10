from ninja import Schema


class SignUpRequestIn(Schema):
    email: str
    code: str
    nickname: str
    password: str
    password_confirm: str

    class Config:
        schema_extra = {
            "email": "test1234@testcom",
            "code": "YWJjZGU=",
            "nickname": "my nickname",
            "password": "testpassword%*",
            "password_confirm": "testpassword%*",
        }


class SignUpRequestOut(Schema):
    email: str
    nickname: str


class ErrorResponse(Schema):
    message: str
