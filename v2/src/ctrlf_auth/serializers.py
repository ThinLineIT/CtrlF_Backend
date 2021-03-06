from ctrlf_auth.constants import (
    MSG_EXPIRED_VERIFICATION_CODE,
    MSG_NOT_EXIST_VERIFICATION_CODE,
    MSG_NOT_MATCHED_PASSWORD,
    MSG_VERIFICATION_CODE_NOT_MATCHED,
    VERIFICATION_TIMEOUT_SECONDS,
)
from ctrlf_auth.models import CtrlfUser, EmailAuthCode
from django.contrib.auth.hashers import check_password
from django.core import signing
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework_jwt.serializers import jwt_payload_handler
from rest_framework_jwt.utils import jwt_encode_handler

from .helpers import CODE_MAX_LENGTH, decode_signing_token


class LoginRequestBody(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


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

        return {"token": jwt_encode_handler(payload), "user": user}


class SignUpSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=30)
    password = serializers.CharField()
    password_confirm = serializers.CharField()
    signing_token = serializers.CharField()

    def validate(self, request_data):
        if request_data["password"] != request_data["password_confirm"]:
            raise ValidationError("패스워드가 일치하지 않습니다.")

        signed_values = signing.loads(request_data["signing_token"])
        if CtrlfUser.objects.filter(email=signed_values["email"]).exists():
            raise ValidationError("중복된 email 입니다.")

        if not EmailAuthCode.objects.filter(code=signed_values["code"]).exists():
            raise ValidationError("유효하지 않은 코드 입니다.")
        return request_data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        signed_token = signing.loads(validated_data.pop("signing_token"))
        validated_data["email"] = signed_token["email"]
        user = CtrlfUser.objects.create(**validated_data)
        user.set_password(validated_data.pop("password"))
        user.save()
        return user


class SendingAuthEmailSerializer(serializers.Serializer):
    email = serializers.CharField()

    def validate_email(self, email):
        try:
            validate_email(email)
        except DjangoValidationError:
            raise DjangoValidationError("유효하지 않은 이메일 형식 입니다.")
        return email


class SendingAuthEmailResponse(serializers.Serializer):
    signing_token = serializers.CharField()


class NicknameDuplicateSerializer(serializers.Serializer):
    _INVALID_ERR_MESSAGE = "전달 된 값이 올바르지 않습니다.\n영어,숫자,한글2~10자\n특수문자x\n공백x"
    _VALID_REGEX = "^[a-zA-Z0-9가-힣]{2,10}$"
    data = serializers.RegexField(regex=_VALID_REGEX, error_messages={"invalid": _INVALID_ERR_MESSAGE})

    def validate_data(self, nickname):
        if CtrlfUser.objects.filter(nickname=nickname).exists():
            raise ValidationError("이미 존재하는 닉네임입니다.")
        return nickname


class CheckEmailDuplicateSerializer(serializers.Serializer):
    data = serializers.CharField()

    def validate_data(self, input_email):
        if CtrlfUser.objects.filter(email=input_email).exists():
            raise ValidationError("이미 존재하는 이메일 입니다.", code=status.HTTP_404_NOT_FOUND)
        try:
            validate_email(input_email)
        except DjangoValidationError:
            raise DjangoValidationError("이메일 형식이 유효하지 않습니다.", code=status.HTTP_400_BAD_REQUEST)
        return input_email


class CheckVerificationCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=CODE_MAX_LENGTH, error_messages={"max_length": "인증코드가 유효하지 않습니다."})
    signing_token = serializers.CharField()

    def validate(self, data):
        if not EmailAuthCode.objects.filter(code=data["code"]).exists():
            raise ValidationError(MSG_NOT_EXIST_VERIFICATION_CODE)
        try:
            decoded = decode_signing_token(token=data["signing_token"], max_age=VERIFICATION_TIMEOUT_SECONDS)
        except ValueError:
            raise ValidationError(MSG_EXPIRED_VERIFICATION_CODE)
        else:
            if decoded["code"] != data["code"]:
                raise ValidationError(MSG_VERIFICATION_CODE_NOT_MATCHED)
        return data


class CheckVerificationCodeResponse(serializers.Serializer):
    signing_token = serializers.CharField()


class LoginResponse(serializers.Serializer):
    token = serializers.CharField()
    user_id = serializers.IntegerField()


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    new_password_confirm = serializers.CharField()
    signing_token = serializers.CharField()

    def validate(self, data):
        new_password = data["new_password"]
        new_password_confirm = data["new_password_confirm"]
        if new_password != new_password_confirm:
            raise ValidationError(MSG_NOT_MATCHED_PASSWORD)
        return data
