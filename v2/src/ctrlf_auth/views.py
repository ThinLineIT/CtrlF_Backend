from ctrlf_auth.serializers import LoginSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.views import ObtainJSONWebTokenView


class LoginAPIView(ObtainJSONWebTokenView):

    serializer_class = LoginSerializer

    @swagger_auto_schema(method="post")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get("user") or request.user
        token = serializer.validated_data.get("token")
        issued_at = serializer.validated_data.get("issued_at")

        return Response(
            JSONWebTokenAuthentication.jwt_create_response_payload(token, user, request, issued_at),
            status=status.HTTP_201_CREATED,
        )
