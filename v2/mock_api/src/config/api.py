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
    NoteCreateResponse,
    NoteRequestBody,
    NoteResponse,
    SendEmailAuthIn,
    SendEmailAuthOut,
    SignUpRequestIn,
    SignUpRequestOut,
    VerificationCodeCheck400Response,
    VerificationCodeCheckResponse,
    VerificationCodeRequestBody,
)
from ninja import NinjaAPI, Router

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


@api.get("/notes", summary="전체 Note 리스트", response={200: NoteResponse})
def retrieve_notes_list(request, cursor: int):
    return (
        200,
        NoteResponse(
            next_cursor=cursor + 30,
            notes=[
                {"id": 1 + cursor, "title": "컴퓨터 네트워크", "status": "NOT_APPROVED"},
                {"id": 2 + cursor, "title": "자료구조", "status": "NOT_APPROVED"},
                {"id": 3 + cursor, "title": "알고리즘", "status": "APPROVED"},
                {"id": 4 + cursor, "title": "운영체제", "status": "APPROVED"},
                {"id": 5 + cursor, "title": "컴퓨터 구조", "status": "APPROVED"},
                {"id": 6 + cursor, "title": "컴파일러", "status": "APPROVED"},
                {"id": 7 + cursor, "title": "이산수학", "status": "APPROVED"},
                {"id": 8 + cursor, "title": "디지털 논리 회로", "status": "APPROVED"},
                {"id": 9 + cursor, "title": "프로그래밍 언어", "status": "APPROVED"},
                {"id": 10 + cursor, "title": "소프트웨어 공학", "status": "APPROVED"},
                {"id": 11 + cursor, "title": "알고리즘", "status": "APPROVED"},
                {"id": 12 + cursor, "title": "자료구조", "status": "NOT_APPROVED"},
                {"id": 13 + cursor, "title": "컴퓨터 네트워크", "status": "NOT_APPROVED"},
                {"id": 14 + cursor, "title": "컴퓨터 구조", "status": "APPROVED"},
                {"id": 15 + cursor, "title": "컴퓨터 네트워크", "status": "NOT_APPROVED"},
                {"id": 16 + cursor, "title": "자료구조", "status": "NOT_APPROVED"},
                {"id": 17 + cursor, "title": "알고리즘", "status": "APPROVED"},
                {"id": 18 + cursor, "title": "운영체제", "status": "APPROVED"},
                {"id": 19 + cursor, "title": "컴퓨터 구조", "status": "APPROVED"},
                {"id": 20 + cursor, "title": "컴파일러", "status": "APPROVED"},
                {"id": 21 + cursor, "title": "이산수학", "status": "APPROVED"},
                {"id": 22 + cursor, "title": "디지털 논리 회로", "status": "APPROVED"},
                {"id": 23 + cursor, "title": "프로그래밍 언어", "status": "APPROVED"},
                {"id": 24 + cursor, "title": "소프트웨어 공학", "status": "APPROVED"},
                {"id": 25 + cursor, "title": "알고리즘", "status": "APPROVED"},
                {"id": 26 + cursor, "title": "자료구조", "status": "NOT_APPROVED"},
                {"id": 27 + cursor, "title": "컴퓨터 네트워크", "status": "NOT_APPROVED"},
                {"id": 28 + cursor, "title": "컴퓨터 구조", "status": "APPROVED"},
                {"id": 29 + cursor, "title": "자료구조", "status": "NOT_APPROVED"},
                {"id": 30 + cursor, "title": "알고리즘", "status": "APPROVED"},
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
    return 201, {"message": "Note가 생성 되었습니다."}


@api.post(
    "/verification-code/check",
    summary="인증코드 검증",
    response={200: VerificationCodeCheckResponse, 400: VerificationCodeCheck400Response},
)
def check_valid_verification_code(request, request_body: VerificationCodeRequestBody):
    return 200, {"message": "유효한 인증코드 입니다."}
