from typing import List

from config.constants import MOCK_ACCESS_TOKEN
from config.schema import (
    EmailDuplicateCheckOut,
    ErrorduplicateEmail400Response,
    ErrorduplicateEmail404Response,
    ErrorduplicateNickName400Response,
    ErrorduplicateNickName404Response,
    ErrorLogin400Response,
    ErrorLogin404Response,
    ErrorLogout400Response,
    ErrorLogout404Response,
    ErrorNoteCreate400Response,
    ErrorSendEmail400Response,
    ErrorSignUp400Response,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    MainEtcInfoResponse,
    NickNameDuplicateCheckOut,
    Note,
    NoteCreateResponse,
    NoteListResponse,
    NoteRequestBody,
    SendEmailAuthIn,
    SendEmailAuthOut,
    SignUpRequestIn,
    SignUpRequestOut,
    VerificationCodeCheck400Response,
    VerificationCodeCheckResponse,
    VerificationCodeRequestBody,
)
from ninja import NinjaAPI, Router

from .schema import CtrlfIssueStatus, IssueListOut

api = NinjaAPI(title="CtrlF Mock API Doc")
api_auth = Router(tags=["인증(SignUp, Login, Logout)"])
api.add_router("/auth/", api_auth)


@api_auth.post("/signup", summary="회원가입", response={200: SignUpRequestOut, 400: ErrorSignUp400Response})
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
    response={200: EmailDuplicateCheckOut, 400: ErrorduplicateEmail400Response, 404: ErrorduplicateEmail404Response},
)
def check_duplicate_email(request, data):
    return 200, {"message": "사용 가능한 이메일 입니다."}


@api_auth.post("/signup/email", summary="인증 이메일 보내기", response={200: SendEmailAuthOut, 400: ErrorSendEmail400Response})
def send_auth_email(request, request_body: SendEmailAuthIn):
    return 200, {"message": "인증 메일이 발송되었습니다."}


@api_auth.post(
    "/login", summary="로그인", response={200: LoginResponse, 400: ErrorLogin400Response, 404: ErrorLogin404Response}
)
def login(request, request_body: LoginRequest):
    return 200, {"token": MOCK_ACCESS_TOKEN}


@api_auth.post(
    "/logout", summary="로그아웃", response={200: LogoutResponse, 400: ErrorLogout400Response, 404: ErrorLogout404Response}
)
def logout(request, request_body: LogoutRequest):
    return 200, {"message": "로그아웃 되었습니다."}


@api.get("/notes/{note_id}", summary="Note 디테일 API", response={200: Note})
def retrieve_notes(request, note_id: int):
    temp_note_map = {
        1: {"id": note_id, "title": "컴퓨터 네트워크", "is_approved": False},
        2: {"id": note_id, "title": "자료구조", "is_approved": False},
        3: {"id": note_id, "title": "알고리즘", "is_approved": True},
        4: {"id": note_id, "title": "운영체제", "is_approved": True},
        5: {"id": note_id, "title": "컴퓨터 구조", "is_approved": True},
        6: {"id": note_id, "title": "컴파일러", "is_approved": True},
        7: {"id": note_id, "title": "이산수학", "is_approved": True},
        8: {"id": note_id, "title": "디지털 논리 회로", "is_approved": True},
        9: {"id": note_id, "title": "프로그래밍 언어", "is_approved": True},
        10: {"id": note_id, "title": "소프트웨어 공학", "is_approved": True},
        11: {"id": note_id, "title": "알고리즘", "is_approved": True},
        12: {"id": note_id, "title": "자료구조", "is_approved": False},
        13: {"id": note_id, "title": "컴퓨터 네트워크", "is_approved": False},
        14: {"id": note_id, "title": "컴퓨터 구조", "is_approved": True},
        15: {"id": note_id, "title": "컴퓨터 네트워크", "is_approved": False},
        16: {"id": note_id, "title": "자료구조", "is_approved": False},
        17: {"id": note_id, "title": "알고리즘", "is_approved": True},
        18: {"id": note_id, "title": "운영체제", "is_approved": True},
        19: {"id": note_id, "title": "컴퓨터 구조", "is_approved": True},
        20: {"id": note_id, "title": "컴파일러", "is_approved": True},
        21: {"id": note_id, "title": "이산수학", "is_approved": True},
        22: {"id": note_id, "title": "디지털 논리 회로", "is_approved": True},
        23: {"id": note_id, "title": "프로그래밍 언어", "is_approved": True},
        24: {"id": note_id, "title": "소프트웨어 공학", "is_approved": True},
        25: {"id": note_id, "title": "알고리즘", "is_approved": True},
        26: {"id": note_id, "title": "자료구조", "is_approved": False},
        27: {"id": note_id, "title": "컴퓨터 네트워크", "is_approved": False},
        28: {"id": note_id, "title": "컴퓨터 구조", "is_approved": True},
        29: {"id": note_id, "title": "자료구조", "is_approved": False},
    }
    result = note_id % 30

    if result:
        return 200, temp_note_map[result]
    else:
        return 200, {"id": note_id, "title": "알고리즘", "is_approved": True}


@api.get("/notes", summary="전체 Note 리스트", response={200: NoteListResponse})
def retrieve_notes_list(request, cursor: int):
    return (
        200,
        NoteListResponse(
            next_cursor=cursor + 30,
            notes=[
                {"id": 1 + cursor, "title": "컴퓨터 네트워크", "is_approved": False},
                {"id": 2 + cursor, "title": "자료구조", "is_approved": False},
                {"id": 3 + cursor, "title": "알고리즘", "is_approved": True},
                {"id": 4 + cursor, "title": "운영체제", "is_approved": True},
                {"id": 5 + cursor, "title": "컴퓨터 구조", "is_approved": True},
                {"id": 6 + cursor, "title": "컴파일러", "is_approved": True},
                {"id": 7 + cursor, "title": "이산수학", "is_approved": True},
                {"id": 8 + cursor, "title": "디지털 논리 회로", "is_approved": True},
                {"id": 9 + cursor, "title": "프로그래밍 언어", "is_approved": True},
                {"id": 10 + cursor, "title": "소프트웨어 공학", "is_approved": True},
                {"id": 11 + cursor, "title": "알고리즘", "is_approved": True},
                {"id": 12 + cursor, "title": "자료구조", "is_approved": False},
                {"id": 13 + cursor, "title": "컴퓨터 네트워크", "is_approved": False},
                {"id": 14 + cursor, "title": "컴퓨터 구조", "is_approved": True},
                {"id": 15 + cursor, "title": "컴퓨터 네트워크", "is_approved": False},
                {"id": 16 + cursor, "title": "자료구조", "is_approved": False},
                {"id": 17 + cursor, "title": "알고리즘", "is_approved": True},
                {"id": 18 + cursor, "title": "운영체제", "is_approved": True},
                {"id": 19 + cursor, "title": "컴퓨터 구조", "is_approved": True},
                {"id": 20 + cursor, "title": "컴파일러", "is_approved": True},
                {"id": 21 + cursor, "title": "이산수학", "is_approved": True},
                {"id": 22 + cursor, "title": "디지털 논리 회로", "is_approved": True},
                {"id": 23 + cursor, "title": "프로그래밍 언어", "is_approved": True},
                {"id": 24 + cursor, "title": "소프트웨어 공학", "is_approved": True},
                {"id": 25 + cursor, "title": "알고리즘", "is_approved": True},
                {"id": 26 + cursor, "title": "자료구조", "is_approved": False},
                {"id": 27 + cursor, "title": "컴퓨터 네트워크", "is_approved": False},
                {"id": 28 + cursor, "title": "컴퓨터 구조", "is_approved": True},
                {"id": 29 + cursor, "title": "자료구조", "is_approved": False},
                {"id": 30 + cursor, "title": "알고리즘", "is_approved": True},
            ],
        ),
    )


@api.get("/notes/other-info", summary="메인화면 기타 정보", response={200: MainEtcInfoResponse})
def retrieve_main_etc_info(request):
    return (
        200,
        MainEtcInfoResponse(
            all_issues_count=20,
            approved_issues_count=10,
            not_approved_issues_count=30,
            not_approved_issues=[{"title": "운영체제"}, {"title": "프로세스는 무엇인가?"}],
        ),
    )


@api.post("/notes", summary="note 생성", response={201: NoteCreateResponse, 400: ErrorNoteCreate400Response})
def create_note(request, request_body: NoteRequestBody):
    return 201, {"message": "새 Note가 생성 되었습니다."}


@api.post(
    "/verification-code/check",
    summary="인증코드 검증",
    response={200: VerificationCodeCheckResponse, 400: VerificationCodeCheck400Response},
)
def check_valid_verification_code(request, request_body: VerificationCodeRequestBody):
    return 200, {"message": "유효한 인증코드 입니다."}


@api.get(
    "/issues",
    summary="Issue 리스트 보기",
    response={200: List[IssueListOut]},
)
def retrieve_issue_list(request):
    return 200, [
        {
            "id": 1,
            "owner": 1,
            "title": "1계층",
            "content": "네트와크 계층 ~~~ ",
            "status": CtrlfIssueStatus.REQUESTED,
            "content_request": {
                "user": 4,
                "type": "PAGE",
                "action": "UPDATE",
                "reason": "7계층 이름에 오타가 있습니다",
                "sub_id": 3,
            },
        },
        {
            "id": 2,
            "owner": 1,
            "title": "운영체제",
            "content": "",
            "status": CtrlfIssueStatus.APPROVED,
            "content_request": {
                "user": 3,
                "type": "NOTE",
                "action": "CREATE",
                "reason": "운영체제가 없는 것 같아서 신청합니다",
                "sub_id": None,
            },
        },
        {
            "id": 3,
            "owner": 2,
            "title": "자료구조",
            "content": "",
            "status": CtrlfIssueStatus.REJECTED,
            "content_request": {
                "user": 2,
                "type": "TOPIC",
                "action": "CREATE",
                "reason": "네트워크에 자료구조가 없는 것 같아 생성 요청합니다.",
                "sub_id": None,
            },
        },
        {
            "id": 4,
            "owner": 1,
            "title": "OSI 7계층",
            "content": "",
            "status": CtrlfIssueStatus.CLOSED,
            "content_request": {
                "user": 1,
                "type": "TOPIC",
                "action": "DELETE",
                "reason": "중복 생성되어서 삭제하려고 합니다.",
                "sub_id": 1,
            },
        },
    ]
