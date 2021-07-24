from ctrlf_auth.models import CtrlfUser
from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler


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

        payload = jwt_payload_handler(user)

        return {
            "token": jwt_encode_handler(payload),
            "user": user,
        }


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    nickname = serializers.CharField(max_length=30)
    password = serializers.CharField()
    code = serializers.CharField(max_length=20)
    password_confirm = serializers.CharField()

    def validate(self, request_data):
        email = request_data["email"]
        if CtrlfUser.objects.filter(email=email).exists():
            raise ValidationError("중복된 email 입니다.")

        password = request_data["password"]
        password_confirm = request_data["password_confirm"]

        if password != password_confirm:
            raise ValidationError("패스워드가 일치하지 않습니다.")
        return request_data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        validated_data.pop("code")

        user = CtrlfUser.objects.create(**validated_data)
        user.set_password(validated_data.pop("password"))
        user.save()
        return user
