from ninja import Schema


class SignUpRequestIn(Schema):
    email: str
    code: str
    nickname: str
    password: str
    password_confirm: str


class SignUpRequestOut(Schema):
    email: str
    nickname: str


class ErrorResponse(Schema):
    message: str
