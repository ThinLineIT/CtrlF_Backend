from rest_framework import serializers

from .models import (
    CtrlfContentType,
    Issue,
    Note,
    Page,
    PageHistory,
    PageVersionType,
    Topic,
)


class NoteListSerializer(serializers.ListSerializer):
    pass


class NoteUpdateRequestBodySerializer(serializers.Serializer):
    new_title = serializers.CharField()
    reason = serializers.CharField()


class NoteUpdateResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


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
        related_model_id = validated_data.pop("related_model").id
        issue = Issue.objects.create(owner=owner, related_model_id=related_model_id, **validated_data)
        return issue


class NoteCreateRequestBodySerializer(serializers.Serializer):
    title = serializers.CharField()
    reason = serializers.CharField(help_text="이슈의 reason에 대한 내용")


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


class TopicUpdateRequestBodySerializer(serializers.Serializer):
    new_title = serializers.CharField()
    reason = serializers.CharField()


class TopicUpdateResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class TopicCreateRequestBodySerializer(serializers.Serializer):
    note_id = serializers.IntegerField()
    title = serializers.CharField()
    reason = serializers.CharField(help_text="이슈의 reason에 대한 내용")


class PageSerializer(serializers.ModelSerializer):
    issue_id = serializers.SerializerMethodField(method_name="get_issue_id")

    class Meta:
        model = Page
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        owner = validated_data["owners"][0]
        page = super().create(validated_data)
        page_history_data = {
            "owner": owner,
            "title": validated_data["title"],
            "content": validated_data["content"],
            "page": page,
            "version_type": PageVersionType.CURRENT,
        }
        page_history = PageHistory.objects.create(**page_history_data)
        return page_history

    def get_issue_id(self, page):
        issue = Issue.objects.filter(related_model_id=page.id, related_model_type=CtrlfContentType.PAGE).first()
        if issue is None:
            return None
        return issue.id


class PageListSerializer(serializers.ModelSerializer):
    version_no = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ["id", "owners", "topic", "title", "is_approved", "version_no"]

    def get_version_no(self, page):
        page_history = page.pagehistory_set.filter(version_type="LATEST")

        if len(page_history) == 0:
            return 1

        return page_history[0].version_no


class PageCreateRequestBodySerializer(serializers.Serializer):
    topic_id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()
    reason = serializers.CharField(help_text="이슈의 reason에 대한 내용")


class PageDetailQuerySerializer(serializers.Serializer):
    version_no = serializers.IntegerField()


class IssueListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    reason = serializers.CharField()
    status = serializers.CharField()
    related_model_type = serializers.CharField()
    action = serializers.CharField()


class IssueDetailSerializer(serializers.Serializer):
    note_id = serializers.SerializerMethodField()
    topic_id = serializers.SerializerMethodField()
    page_id = serializers.SerializerMethodField()
    version_no = serializers.SerializerMethodField()

    id = serializers.IntegerField()
    owner = serializers.EmailField()
    title = serializers.CharField()
    reason = serializers.CharField()
    status = serializers.CharField()
    related_model_type = serializers.CharField()
    action = serializers.CharField()
    legacy_title = serializers.SerializerMethodField()

    def get_legacy_title(self, issue):
        return issue.etc or ""

    def get_page_id(self, issue):
        if issue.related_model_type == CtrlfContentType.PAGE:
            return PageHistory.objects.get(id=issue.related_model_id).page.id
        return None

    def get_topic_id(self, issue):
        if issue.related_model_type == CtrlfContentType.TOPIC:
            return issue.related_model_id
        elif issue.related_model_type == CtrlfContentType.PAGE:
            page = Page.objects.get(id=issue.related_model_id)
            return Topic.objects.get(id=page.topic.id).id
        else:
            return None

    def get_note_id(self, issue):
        if issue.related_model_type == CtrlfContentType.NOTE:
            return issue.related_model_id
        elif issue.related_model_type == CtrlfContentType.TOPIC:
            topic = Topic.objects.get(id=issue.related_model_id)
        else:
            page = Page.objects.get(id=issue.related_model_id)
            topic = Topic.objects.get(id=page.topic.id)
        return Note.objects.get(id=topic.note.id).id

    def get_version_no(self, issue):
        if issue.related_model_type != CtrlfContentType.PAGE:
            return None
        page_history = PageHistory.objects.get(id=issue.related_model_id)
        return page_history.version_no


class IssueApproveResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class IssueApproveRequestBodySerializer(serializers.Serializer):
    issue_id = serializers.IntegerField()


class ImageUploadRequestBodySerializer(serializers.Serializer):
    image = serializers.ImageField()


class ImageSerializer(serializers.Serializer):
    img_url = serializers.CharField()
