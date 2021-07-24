from ctrlf_auth.serializers import LoginSerializer, SignUpSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.views import ObtainJSONWebTokenView


class LoginAPIView(ObtainJSONWebTokenView):

    serializer_class = LoginSerializer

    @swagger_auto_schema(method="post")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(data={"token": serializer.validated_data.get("token")}, status=status.HTTP_200_OK)


class SignUpAPIView(APIView):
    _SIGNUP_MSG = "환영합니다.\n가입이 완료되었습니다\n\n로그인 후 이용해주세요."

    def post(self, request, *args, **kwargs):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={"message": self._SIGNUP_MSG}, status=status.HTTP_201_CREATED)
