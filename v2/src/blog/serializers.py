from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Post


class PostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"

    def validate(self, data):
        try:
            pass
        except User.DoesNotExist as author_not_exist:
            raise serializers.ValidationError("author를 찾을 수 없습니다.") from author_not_exist

        if not data["title"]:
            raise serializers.ValidationError("title이 없습니다.")

        if not data["text"]:
            raise serializers.ValidationError("text가 없습니다.")

        return data
