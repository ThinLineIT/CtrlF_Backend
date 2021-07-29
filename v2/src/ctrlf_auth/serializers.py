from ctrlf_auth.models import CtrlfUser, EmailAuthCode
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
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

        return {"token": jwt_encode_handler(payload), "user": user}


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    nickname = serializers.CharField(max_length=30)
    password = serializers.CharField()
    code = serializers.CharField(max_length=20)
    password_confirm = serializers.CharField()

    def validate(self, request_data):
        if CtrlfUser.objects.filter(email=request_data["email"]).exists():
            raise ValidationError("중복된 email 입니다.")

        if request_data["password"] != request_data["password_confirm"]:
            raise ValidationError("패스워드가 일치하지 않습니다.")

        if not EmailAuthCode.objects.filter(code=request_data["code"]).exists():
            raise ValidationError("유효하지 않은 코드 입니다.")
        return request_data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        validated_data.pop("code")

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


class NicknameDuplicateSerializer(serializers.Serializer):
    _INVALID_ERR_MESSAGE = "전달 된 값이 올바르지 않습니다.\n영어,숫자,한글2~10자\n특수문자x\n공백x"
    _VALID_REGEX = "^[a-zA-Z0-9ㅏ-ㅣㄱ-ㅎ가-힣]{2,10}$"
    data = serializers.RegexField(regex=_VALID_REGEX, error_messages={"invalid": _INVALID_ERR_MESSAGE})

    def validate_data(self, nickname):
        if CtrlfUser.objects.filter(nickname=nickname).exists():
            raise ValidationError("이미 존재하는 닉네임입니다.")
        return nickname
