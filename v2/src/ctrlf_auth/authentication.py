import jwt
from ctrlf_auth.models import CtrlfUser
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework_jwt.settings import api_settings


class CtrlfAuthentication(BaseAuthentication):
    def _decode_token(self, token) -> dict:
        return jwt.decode(
            jwt=token.decode("utf-8"),
            key=api_settings.JWT_SECRET_KEY,
            algorithms=[api_settings.JWT_ALGORITHM],
        )

    def authenticate(self, request):
        auth_key, raw_token = get_authorization_header(request).split()
        payload = self._decode_token(raw_token)
        return CtrlfUser.objects.get(email=payload["email"]), raw_token
