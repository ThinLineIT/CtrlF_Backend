from datetime import datetime
from typing import List, Optional

from django.db import models
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
    token: str


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


class Note(Schema):
    id: int
    title: str
    is_approved: bool


class NoteListResponse(Schema):
    next_cursor: int
    notes: List[Note]

    class Config:
        schema_extra = {
            "example": {
                "next_cursor": 30,
                "notes": [
                    {"id": 1, "title": "컴퓨터 네트워크", "is_approved": False},
                    {"id": 2, "title": "자료구조", "is_approved": False},
                    {"id": 3, "title": "알고리즘", "is_approved": True},
                    {"id": 4, "title": "운영체제", "is_approved": True},
                    {"id": 5, "title": "컴퓨터 구조", "is_approved": True},
                    {"id": 6, "title": "컴파일러", "is_approved": True},
                    {"id": 7, "title": "이산수학", "is_approved": True},
                    {"id": 8, "title": "디지털 논리 회로", "is_approved": True},
                    {"id": 9, "title": "프로그래밍 언어", "is_approved": True},
                    {"id": 10, "title": "소프트웨어 공학", "is_approved": True},
                    {"id": 11, "title": "알고리즘", "is_approved": True},
                    {"id": 12, "title": "자료구조", "is_approved": False},
                    {"id": 13, "title": "컴퓨터 네트워크", "is_approved": False},
                    {"id": 14, "title": "컴퓨터 구조", "is_approved": True},
                    {"id": 15, "title": "컴퓨터 네트워크", "is_approved": False},
                    {"id": 16, "title": "자료구조", "is_approved": False},
                    {"id": 17, "title": "알고리즘", "is_approved": True},
                    {"id": 18, "title": "운영체제", "is_approved": True},
                    {"id": 19, "title": "컴퓨터 구조", "is_approved": True},
                    {"id": 20, "title": "컴파일러", "is_approved": True},
                    {"id": 21, "title": "이산수학", "is_approved": True},
                    {"id": 22, "title": "디지털 논리 회로", "is_approved": True},
                    {"id": 23, "title": "프로그래밍 언어", "is_approved": True},
                    {"id": 24, "title": "소프트웨어 공학", "is_approved": True},
                    {"id": 25, "title": "알고리즘", "is_approved": True},
                    {"id": 26, "title": "자료구조", "is_approved": False},
                    {"id": 27, "title": "컴퓨터 네트워크", "is_approved": False},
                    {"id": 28, "title": "컴퓨터 구조", "is_approved": True},
                    {"id": 29, "title": "자료구조", "is_approved": False},
                    {"id": 30, "title": "알고리즘", "is_approved": True},
                ],
            }
        }


class Issue(Schema):
    title: str


class MainEtcInfoResponse(Schema):
    not_approved_issues: List[Issue]
    all_issues_count: int
    approved_issues_count: int
    not_approved_issues_count: int


class NoteRequestBody(Schema):
    title: str
    request_contents: str

    class Config:
        schema_extra = {"example": {"title": "운영체제", "request_contents": "운영체제 노트가 없네요 추가 요청 합니다:)"}}


class NoteCreateResponse(Schema):
    message: str


class ErrorNoteCreate400Response(Schema):
    message: str

    class Config:
        schema_extra = {"example": {"request body가 유효하지 않음": {"message": "제목과 내용을 채워주세요."}}}


class VerificationCodeCheckResponse(Schema):
    message: str


class VerificationCodeCheck400Response(Schema):
    message: str

    class Config:
        schema_extra = {"example": {"전달된 값이 유효하지 않을 때": {"message": "인증코드가 올바르지 않습니다."}}}


class VerificationCodeRequestBody(Schema):
    code: str


class CtrlfIssueStatus(models.TextChoices):
    REQUESTED = "REQUESTED", "요청"
    REJECTED = "REJECTED", "거절"
    APPROVED = "APPROVED", "승인"
    CLOSED = "CLOSED", "닫힘"


class CtrlfActionType(models.TextChoices):
    CREATE = "CREATE", "생성"
    UPDATE = "UPDATE", "수정"
    DELETE = "DELETE", "삭제"


class CtrlfContentType(models.TextChoices):
    NOTE = "NOTE", "노트"
    TOPIC = "TOPIC", "토픽"
    PAGE = "PAGE", "페이지"


class ContentRequest(Schema):
    user_id: int
    type: CtrlfContentType
    action: CtrlfActionType
    reason: str
    sub_id: Optional[int]


class IssueListOut(Schema):
    id: int
    owner_id: int
    title: str
    content: str
    status: CtrlfIssueStatus
    content_request: ContentRequest


class TopicListOut(Schema):
    id: int
    title: str
    created_at: datetime
    is_approved: bool
    owner_id: int


class PageListOut(Schema):
    id: int
    title: str
    content: str
    created_at: datetime
    is_approved: bool
    owners: List[int]
