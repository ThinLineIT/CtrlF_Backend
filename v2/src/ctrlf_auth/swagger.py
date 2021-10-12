from ctrlf_auth.serializers import (
    CheckEmailDuplicateSerializer,
    CheckVerificationCodeResponse,
    CheckVerificationCodeSerializer,
    LoginRequestBody,
    NicknameDuplicateSerializer,
    ResetPasswordSerializer,
    SendingAuthEmailResponse,
    SendingAuthEmailSerializer,
    SignUpSerializer,
)

SWAGGER_RESET_PASSWORD_VIEW = {
    "request_body": ResetPasswordSerializer,
    "operation_summary": "비밀번호 재설정 API",
    "operation_description": "'비밀번호'와 '비밀번호 확인'을 받아 비밀번호를 재설정 합니다",
    "tags": ["비밀번호 찾기"],
}

SWAGGER_CHECK_VERIFICATION_CODE_VIEW = {
    "request_body": CheckVerificationCodeSerializer,
    "operation_summary": "인증코드 확인 API",
    "operation_description": "전달받은 인증코드가 유효한지 체크 합니다",
    "responses": {"200": CheckVerificationCodeResponse},
    "tags": ["회원가입"],
}

SWAGGER_CHECK_EMAIL_DUPLICATE_VIEW = {
    "query_serializer": CheckEmailDuplicateSerializer,
    "operation_summary": "이메일 중복체크 API",
    "operation_description": "이메일이 중복인지 체크 합니다",
    "tags": ["회원가입"],
}

SWAGGER_CHECK_NICKNAME_DUPLICATE_VIEW = {
    "query_serializer": NicknameDuplicateSerializer,
    "operation_summary": "닉네임 중복체크 API",
    "operation_description": "닉네임이 중복인지 체크 합니다",
    "tags": ["회원가입"],
}

SWAGGER_SENDING_AUTH_EMAIL_VIEW = {
    "request_body": SendingAuthEmailSerializer,
    "operation_summary": "인증메일 보내기 API",
    "operation_description": "회원가입을 원하는 사용자에게 인증메일을 전달 합니다",
    "responses": {"200": SendingAuthEmailResponse},
    "tags": ["회원가입"],
}

SWAGGER_SIGN_UP_API_VIEW = {
    "request_body": SignUpSerializer,
    "operation_summary": "회원가입 API",
    "operation_description": "사용자 정보를 받아서, 회원가입 합니다",
    "tags": ["회원가입"],
}

SWAGGER_LOGIN_API_VIEW = {
    "request_body": LoginRequestBody,
    "operation_summary": "로그인 API",
    "operation_description": "email과 password를 받아서, Login 합니다",
    "tags": ["로그인"],
}

SWAGGER_TEMP_DELETE_EMAIL_VIEW = {
    "request_body": SendingAuthEmailSerializer,
    "operation_summary": "임시 이메일 삭제 전용 API",
    "operation_description": "임시 사용 목적으로 만든 API 입니다",
    "tags": ["기타"],
}
