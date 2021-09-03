from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from .constants import ERR_NOTE_NOT_FOUND
from .models import (
    ContentRequest,
    CtrlfActionType,
    CtrlfContentType,
    CtrlfIssueStatus,
    Issue,
    Note,
    Page,
    Topic,
)


class NoteListSerializer(serializers.ListSerializer):
    pass


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
        list_serializer_class = NoteListSerializer

    def create(self, validated_data):
        owner = validated_data.pop("owners")[0]
        note = Note.objects.create(**validated_data)
        note.owners.add(owner)
        return note


class IssueCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = "__all__"

    def create(self, validated_data):
        owner = validated_data.pop("owner")
        note = validated_data.pop("note")
        content_request_data = {
            "user": owner,
            "sub_id": note.id,
            "type": CtrlfContentType.NOTE,
            "action": CtrlfActionType.CREATE,
            "reason": "create note",
        }
        content_request = ContentRequest.objects.create(**content_request_data)
        issue = Issue.objects.create(owner=owner, content_request=content_request, **validated_data)
        return issue


class NoteCreateRequestBodySerializer(serializers.Serializer):
    title = serializers.CharField()
    content = serializers.CharField()


class NoteListQuerySerializer(serializers.Serializer):
    cursor = serializers.IntegerField()


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ["id", "created_at", "updated_at", "title", "note", "is_approved"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        owner = validated_data.pop("owner")
        topic = Topic.objects.create(**validated_data)
        topic.owners.add(owner)
        topic.save()
        return topic


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class ContentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentRequest
        fields = "__all__"

    def create(self, validated_data):
        content_request = ContentRequest.objects.create(**validated_data)
        content_request.save()
        return content_request


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = "__all__"

    def create(self, validated_data):
        issue = Issue.objects.create(**validated_data)
        issue.save()
        return issue


class TopicCreateSerializer(serializers.Serializer):
    note = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()

    def validate(self, request_data):
        try:
            Note.objects.get(id=request_data["note"])
        except Note.DoesNotExist:
            raise ValidationError(detail=ERR_NOTE_NOT_FOUND, code=status.HTTP_404_NOT_FOUND)
        return request_data

    def create(self, validated_data):
        topic_data = {
            "note": validated_data["note"],
            "title": validated_data["title"],
        }
        topic = TopicSerializer(data=topic_data)
        if not topic.is_valid():
            raise ValidationError(detail="topic 생성 실패", code=status.HTTP_400_BAD_REQUEST)
        topic = topic.save(owner=validated_data["owner"])

        content_request_data = {
            "type": CtrlfContentType.TOPIC,
            "action": CtrlfActionType.CREATE,
            "sub_id": topic.id,
            "user": validated_data["owner"].id,
        }
        content_request = ContentRequestSerializer(data=content_request_data)
        if not content_request.is_valid():
            raise ValidationError(detail="content_request 생성 실패", code=status.HTTP_400_BAD_REQUEST)
        content_request = content_request.save()

        issue_data = {
            "owner": validated_data["owner"].id,
            "content_request": content_request.id,
            "title": validated_data["title"],
            "content": validated_data["content"],
            "status": CtrlfIssueStatus.REQUESTED,
        }
        issue = IssueSerializer(data=issue_data)
        if not issue.is_valid():
            raise ValidationError(detail="issue 생성 실패", code=status.HTTP_400_BAD_REQUEST)
        issue = issue.save()

        return issue
