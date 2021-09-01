from rest_framework import serializers

from .models import (
    ContentRequest,
    CtrlfActionType,
    CtrlfContentStatus,
    CtrlfContentType,
    Issue,
    Note,
    Page,
    Topic,
)


class ContentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentRequest
        fields = ["user", "sub_id", "type", "action", "reason", "status"]


class IssueSerializer(serializers.ModelSerializer):
    content_request = ContentRequestSerializer()

    class Meta:
        model = Issue
        fields = ["id", "owner", "title", "content", "status", "content_request"]

    def to_representation(self, instance):
        def get_note_owners(note_id, creator):
            note = Note.objects.get(id=note_id)
            serializer = NoteSerializer(note)
            serializered_note = serializer.data

            creator["note"] = serializered_note["owners"]
            return creator

        def get_topic_owners(topic_id, creator):
            topic = Topic.objects.get(id=topic_id)
            serializer = TopicSerializer(topic)
            serializered_topic = serializer.data
            creator["topic"] = serializered_topic["owners"]
            return get_note_owners(serializered_topic["note"], creator)

        def get_page_owners(page_id, creator):
            page = Page.objects.get(id=page_id)
            serializer = PageSerializer(page)
            serializered_page = serializer.data
            creator["page"] = serializered_page["owners"]
            return get_topic_owners(serializered_page["topic"], creator)

        def make_creator(type, target_id):
            creator = {
                "note": None,
                "topic": None,
                "page": None,
            }

            if type == "NOTE":
                creator = get_note_owners(target_id, creator)
            elif type == "TOPIC":
                creator = get_topic_owners(target_id, creator)
            elif type == "PAGE":
                creator = get_page_owners(target_id, creator)

            return creator

        issue = super().to_representation(instance)
        creator = make_creator(issue["content_request"]["type"], issue["content_request"]["sub_id"])

        return {
            "id": issue["id"],
            "title": issue["title"],
            "content": issue["content"],
            "action": issue["content_request"]["action"],
            "content_id": issue["content_request"]["sub_id"],
            "content_type": issue["content_request"]["type"],
            "content_status": issue["content_request"]["status"],
            "issue_status": issue["status"],
            "reason": issue["content_request"]["reason"],
            "creator": creator,
        }


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
            "status": CtrlfContentStatus.PENDING,
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
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
