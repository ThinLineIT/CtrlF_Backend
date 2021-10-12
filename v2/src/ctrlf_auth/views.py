from typing import List

from ctrlf_auth.helpers import generate_auth_code, generate_signing_token
from ctrlf_auth.models import CtrlfUser, EmailAuthCode
from ctrlf_auth.serializers import (
    CheckEmailDuplicateSerializer,
    CheckVerificationCodeResponse,
    CheckVerificationCodeSerializer,
    LoginSerializer,
    NicknameDuplicateSerializer,
    SendingAuthEmailResponse,
    SendingAuthEmailSerializer,
    SignUpSerializer,
)
from ctrlf_auth.swagger import (
    SWAGGER_CHECK_EMAIL_DUPLICATE_VIEW,
    SWAGGER_CHECK_NICKNAME_DUPLICATE_VIEW,
    SWAGGER_CHECK_VERIFICATION_CODE_VIEW,
    SWAGGER_LOGIN_API_VIEW,
    SWAGGER_SENDING_AUTH_EMAIL_VIEW,
    SWAGGER_SIGN_UP_API_VIEW,
    SWAGGER_TEMP_DELETE_EMAIL_VIEW,
)
from ctrlf_auth.tasks import send_email
from django.core import signing
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.views import ObtainJSONWebToken


class LoginAPIView(ObtainJSONWebToken):
    authentication_classes: List[str] = []

    serializer_class = LoginSerializer

    @swagger_auto_schema(**SWAGGER_LOGIN_API_VIEW)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized = serializer.validated_data
        return Response(
            data={"token": serialized["token"], "user_id": serialized["user"].id}, status=status.HTTP_200_OK
        )


class SignUpAPIView(APIView):
    authentication_classes: List[str] = []

    _SIGNUP_MSG = "환영합니다.\n가입이 완료되었습니다\n\n로그인 후 이용해주세요."

    @swagger_auto_schema(**SWAGGER_SIGN_UP_API_VIEW)
    def post(self, request, *args, **kwargs):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={"message": self._SIGNUP_MSG}, status=status.HTTP_201_CREATED)
        else:
            for _, message in serializer.errors.items():
                message = message[0]
        return Response(data={"message": message}, status=status.HTTP_400_BAD_REQUEST)


class SendingAuthEmailView(APIView):
    authentication_classes: List[str] = []

    @swagger_auto_schema(**SWAGGER_SENDING_AUTH_EMAIL_VIEW)
    def post(self, request, *args, **kwargs):
        serializer = SendingAuthEmailSerializer(data=request.data)
        if serializer.is_valid():
            email_auth_code = EmailAuthCode.objects.create(code=generate_auth_code())
            send_email.delay(code=email_auth_code.code, to=serializer.data["email"])
            signing_token = generate_signing_token(data=serializer.data)
            return Response(
                status=status.HTTP_200_OK, data=SendingAuthEmailResponse({"signing_token": signing_token}).data
            )
        else:
            for _, message in serializer.errors.items():
                message = message[0]
        return Response(data={"message": message}, status=status.HTTP_400_BAD_REQUEST)


class TempDeleteEmailView(APIView):
    authentication_classes: List[str] = []

    @swagger_auto_schema(**SWAGGER_TEMP_DELETE_EMAIL_VIEW)
    def delete(self, request):
        serializer = SendingAuthEmailSerializer(data=request.data)
        if serializer.is_valid():
            user = CtrlfUser.objects.get(email=serializer.data["email"])
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class CheckNicknameDuplicateView(APIView):
    authentication_classes: List[str] = []

    _SUCCESS_MSG = "사용 가능한 닉네임입니다."

    @swagger_auto_schema(**SWAGGER_CHECK_NICKNAME_DUPLICATE_VIEW)
    def get(self, request):
        nickname = request.query_params
        serializer = NicknameDuplicateSerializer(data=nickname)
        if serializer.is_valid():
            return Response(data={"message": self._SUCCESS_MSG}, status=status.HTTP_200_OK)
        else:
            for _, message in serializer.errors.items():
                message = message[0]
        return Response(data={"message": message}, status=status.HTTP_400_BAD_REQUEST)


class CheckEmailDuplicateView(APIView):
    authentication_classes: List[str] = []

    @swagger_auto_schema(**SWAGGER_CHECK_EMAIL_DUPLICATE_VIEW)
    def get(self, request):
        serializer = CheckEmailDuplicateSerializer(data=request.query_params)

        if serializer.is_valid():
            return Response({"message": "사용 가능한 이메일 입니다."}, status=status.HTTP_200_OK)
        else:
            for _, message in serializer.errors.items():
                err = message[0]
            return Response({"message": err}, status=err.code)


class CheckVerificationCodeView(APIView):
    authentication_classes: List[str] = []

    @swagger_auto_schema(**SWAGGER_CHECK_VERIFICATION_CODE_VIEW)
    def post(self, request):
        serializer = CheckVerificationCodeSerializer(data=request.data)

        if serializer.is_valid():
            signing_token = generate_signing_token(
                data={
                    "email": signing.loads(serializer.validated_data["signing_token"])["email"],
                    "code": serializer.validated_data["code"],
                }
            )
            return Response(
                status=status.HTTP_200_OK, data=CheckVerificationCodeResponse({"signing_token": signing_token}).data
            )
        else:
            for _, message in serializer.errors.items():
                err = message[0]
            return Response({"message": err}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    authentication_classes: List[str] = []
