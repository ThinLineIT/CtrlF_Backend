from rest_framework import serializers

from .models import CtrlfContentType, Issue, Note, Page, Topic


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
        content_id = validated_data.pop("ctrlf_content").id
        issue = Issue.objects.create(owner=owner, content_id=content_id, **validated_data)
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


class PageListSerializer(PageSerializer):
    issue_id = serializers.SerializerMethodField()

    def get_issue_id(self, obj):
        issue = Issue.objects.filter(content_id=obj.id, content_type=CtrlfContentType.PAGE).first()
        if issue is None:
            return issue
        else:
            return issue.id


class PageCreateRequestBodySerializer(serializers.Serializer):
    topic_id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()
    summary = serializers.CharField()


class IssueSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    owner = serializers.EmailField()
    title = serializers.CharField()
    reason = serializers.CharField()
    status = serializers.CharField()
    content_type = serializers.CharField()
    content_id = serializers.IntegerField()
    action = serializers.CharField()


class IssueDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    owner = serializers.EmailField()
    title = serializers.CharField()
    reason = serializers.CharField()
    status = serializers.CharField()
    content_type = serializers.CharField()
    content_id = serializers.IntegerField()
    action = serializers.CharField()

    def get_note_id(self, obj):
        page = Page.objects.get(id=obj.content_request.sub_id)
        topic = Topic.objects.get(id=page.topic.id)
        return Note.objects.get(id=topic.note.id).id

    def get_topic_id(self, obj):
        page = Page.objects.get(id=obj.content_request.sub_id)
        return Topic.objects.get(id=page.topic.id).id

    def get_page_id(self, obj):
        return Page.objects.get(id=obj.content_request.sub_id).id


class IssueListQuerySerializer(serializers.Serializer):
    cursor = serializers.IntegerField()


class IssueApproveResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class IssueApproveRequestBodySerializer(serializers.Serializer):
    issue_id = serializers.IntegerField()
