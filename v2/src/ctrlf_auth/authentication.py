# import jwt
# from jwt import InvalidTokenError
# from rest_framework.authentication import BaseAuthentication, get_authorization_header
# from rest_framework.exceptions import AuthenticationFailed
#
# from ctrlf_auth.models import CtrlfUser
#
#
# class CtrlfAuthentication(BaseAuthentication):
#     def decode_token(token) -> dict:
#         return jwt.decode(
#             jwt=token.decode("utf-8"),
#             key=settings.AUTHYO_SECRET_KEY,
#             algorithms=[settings.AUTHYO_ALGORITHM],
#         )
#     def authenticate(self, request):
#         try:
#             auth_key, raw_token = get_authorization_header(request).split()
#         except ValueError:
#             raise AuthenticationFailed()
#
#         try:
#             payload = decode_token(raw_token)
#         except InvalidTokenError:
#             raise AuthenticationFailed()
#
#         if not validate_payload(payload):
#             raise AuthenticationFailed()
#         return
#
#
#         if auth_method := auth_method_by_key.get(auth_key.lower()):
#             return auth_method(raw_token)
#         else:
#             raise AuthenticationFailed()
#
#         email = request.META.get("HTTP_X_EMAIL")
#         if not email:
#             return None
#
#         try:
#             user = CtrlfUser.objects.get(email=email)
#         except CtrlfUser.DoesNotExist:
#             raise AuthenticationFailed({"message": "유저 정보를 찾을 수 없습니다"})
#
#         return (user, None)
from rest_framework.authentication import BaseAuthentication


class CtrlfAuthentication(BaseAuthentication):
    def authenticate(self, request):
        print("auth")
        return None
