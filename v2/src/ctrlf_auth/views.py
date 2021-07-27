from ctrlf_auth.helpers import generate_auth_code
from ctrlf_auth.models import EmailAuthCode
from ctrlf_auth.serializers import (
    LoginSerializer,
    SendingAuthEmailSerializer,
    SignUpSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.views import ObtainJSONWebToken


class LoginAPIView(ObtainJSONWebToken):
    serializer_class = LoginSerializer

    @swagger_auto_schema(method="post")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(data={"token": serializer.validated_data.get("token")}, status=status.HTTP_200_OK)


class SignUpAPIView(APIView):
    _SIGNUP_MSG = "환영합니다.\n가입이 완료되었습니다\n\n로그인 후 이용해주세요."

    @swagger_auto_schema(request_body=SignUpSerializer)
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
    @swagger_auto_schema(request_body=SendingAuthEmailSerializer)
    def post(self, request, *args, **kwargs):
        serializer = SendingAuthEmailSerializer(data=request.data)
        if serializer.is_valid():
            email_auth_code = EmailAuthCode.objects.create(code=generate_auth_code())
            success = email_auth_code.send_email(to=serializer.data["email"])
            if not success:
                # TODO: 메일발송 실패 로그 남기기
                pass
            return Response(status=status.HTTP_200_OK)
        else:
            for _, message in serializer.errors.items():
                message = message[0]
        return Response(data={"message": message}, status=status.HTTP_400_BAD_REQUEST)


class CheckNicknameDuplicateView(APIView):
    _SUCCESS_MSG = "사용 가능한 닉네임입니다."

    def get(self, request):
        return Response(status=status.HTTP_200_OK)
