from ctrlf_auth.models import CtrlfUser
from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.utils import unix_epoch


class LoginSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
    token = serializers.CharField(read_only=True)

    def __init__(self, *args, **kwargs):
        """Dynamically add the USERNAME_FIELD to self.fields."""
        super(LoginSerializer, self).__init__(*args, **kwargs)

        self.fields[self.email_field] = serializers.CharField(write_only=True, required=True)

    @property
    def email_field(self):
        return CtrlfUser.USERNAME_FIELD

    def validate(self, data):
        try:
            user = CtrlfUser.objects.get(email=data["email"])
        except CtrlfUser.DoesNotExist:
            raise serializers.ValidationError("이메일이 존재하지 않습니다.")

        if not check_password(data["password"], user.password):
            raise serializers.ValidationError("패스워드가 일치하지 않습니다.")

        payload = JSONWebTokenAuthentication.jwt_create_payload(user)

        return {
            "token": JSONWebTokenAuthentication.jwt_encode_payload(payload),
            "user": user,
            "issued_at": payload.get("iat", unix_epoch()),
        }