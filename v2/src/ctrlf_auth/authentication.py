import jwt
from ctrlf_auth.models import CtrlfUser
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_jwt.settings import api_settings


class CtrlfAuthentication(BaseAuthentication):
    def _decode_token(self, token) -> dict:
        return jwt.decode(
            jwt=token.decode("utf-8"),
            key=api_settings.JWT_SECRET_KEY,
            algorithms=[api_settings.JWT_ALGORITHM],
        )

    def authenticate(self, request):
        try:
            auth_key, raw_token = get_authorization_header(request).split()
        except ValueError:
            raise AuthenticationFailed("인증이 유효하지 않습니다.")

        try:
            payload = self._decode_token(raw_token)
        except jwt.DecodeError:
            raise AuthenticationFailed("인증이 유효하지 않습니다.")

        return CtrlfUser.objects.get(email=payload["email"]), raw_token

    def authenticate_header(self, request):
        return "Basic realm='api'"
