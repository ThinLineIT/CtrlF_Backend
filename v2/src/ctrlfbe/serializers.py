from rest_framework import serializers

from .models import (
    ContentRequest,
    CtrlfActionType,
    CtrlfContentType,
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
        ctrlf_content = validated_data.pop("ctrlf_content")
        content_type = (
            CtrlfContentType.NOTE
            if type(ctrlf_content) is Note
            else CtrlfContentType.TOPIC
            if type(ctrlf_content) is Topic
            else CtrlfContentType.PAGE
        )

        content_request_data = {
            "user": owner,
            "sub_id": ctrlf_content.id,
            "type": content_type,
            "action": CtrlfActionType.CREATE,
            "reason": f"{CtrlfActionType.CREATE} {str(ctrlf_content._meta).split('.')[1]}",
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
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

        def create(self, validated_data):
            owner = validated_data.pop("owners")[0]
            topic = Topic.objects.all(**validated_data)
            topic.owners.add(owner)
            return topic


class TopicCreateRequestBodySerializer(serializers.Serializer):
    note_id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

        def create(self, validated_data):
            owner = validated_data.pop("owners")[0]
            page = Page.objects.create(**validated_data)
            page.owners.add(owner)
            return page


class PageCreateRequestBodySerializer(serializers.Serializer):
    topic_id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()
    summary = serializers.CharField()


class IssueSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    owner = serializers.EmailField()
    title = serializers.CharField()
    content = serializers.CharField()
    status = serializers.CharField()


class IssueListQuerySerializer(serializers.Serializer):
    cursor = serializers.IntegerField()


class IssueApproveResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class IssueApproveRequestBodySerializer(serializers.Serializer):
    issue_id = serializers.IntegerField()
