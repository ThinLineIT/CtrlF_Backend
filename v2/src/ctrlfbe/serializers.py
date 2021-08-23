from ctrlf_auth.models import CtrlfUser
from rest_framework import serializers

from .models import ContentRequest, Issue, Note, Page, Topic


class NoteListSerializer(serializers.ListSerializer):
    pass


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CtrlfUser
        exclude = ["password"]
        extra_kwargs = {
            "email": {"validators": [str]},
        }


class NoteSerializer(serializers.ModelSerializer):
    owners = OwnerSerializer(many=True)

    class Meta:
        model = Note
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
        list_serializer_class = NoteListSerializer

    def create(self, validated_data):
        owner_data = validated_data.pop("owners")
        note = Note.objects.create(**validated_data)
        note.owners.add(CtrlfUser.objects.get(email=owner_data[0].get("email")))
        return note


class ContentRequestSerializer(serializers.ModelSerializer):
    user = OwnerSerializer()

    class Meta:
        model = ContentRequest
        fields = "__all__"

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = CtrlfUser.objects.get(email=user_data.get("email"))
        validated_data["user_id"] = user.id
        content_request = ContentRequest.objects.create(**validated_data)

        return content_request


class IssueCreateSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer()
    content_request = ContentRequestSerializer()

    class Meta:
        model = Issue
        fields = "__all__"

    def create(self, validated_data):
        owner_data = validated_data.pop("owner")
        owner = CtrlfUser.objects.get(email=owner_data.get("email"))

        content_request_data = validated_data.pop("content_request")
        content_request = ContentRequest.objects.get(sub_id=content_request_data.get("sub_id"))

        validated_data["content_request"] = content_request
        validated_data["owner_id"] = owner.id
        issue = Issue.objects.create(**validated_data)
        return issue


class NoteListQuerySerializer(serializers.Serializer):
    cursor = serializers.IntegerField()


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ["id", "title", "created_at", "is_approved", "owners"]
        read_only_fields = ["id", "created_at"]


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
