"""
{
  "user_id": 1,
  "username": "kwon5604@naver.com",
  "exp": 1627863269,
  "email": "kwon5604@naver.com"
}
"""
MOCK_JWT_TOKEN = """eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6Imt3b241NjA0QG5hdmVyLmNvbSIsImV4cCI6MTYyNzg2MzI2OSwiZW1haWwiOiJrd29uNTYwNEBuYXZlci5jb20ifQ.-hs4dfJxt7in9U_f_3VQ3TqtEK0KrsagHWwdcDs8R9I"""  # noqa: E501

SIGNING_TOKEN_MAX_AGE = 600  # seconds
VERIFICATION_TIMEOUT_SECONDS = 300

MSG_EXPIRED_VERIFICATION_CODE = "인증코드가 만료되었습니다."
MSG_NOT_EXIST_VERIFICATION_CODE = "인증코드가 존재하지 않습니다."

MSG_SUCCESS_RESET_PASSWORD = "비밀번호가 정상적으로 재설정 되었습니다."
MSG_NOT_MATCHED_PASSWORD = "입력한 비밀번호가 일치하지 않습니다."
MSG_SUCCESS_SIGN_UP = "환영합니다.\n가입이 완료되었습니다\n\n로그인 후 이용해주세요."

MSG_VERIFICATION_CODE_NOT_MATCHED = "유효하지 않은 인증코드 입니다."
