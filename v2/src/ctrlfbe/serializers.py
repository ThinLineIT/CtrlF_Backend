from django.http import Http404
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


class NoteDeleteRequestBodySerializer(serializers.Serializer):
    reason = serializers.CharField()


class NoteDeleteResponseSerializer(serializers.Serializer):
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


class PageUpdateRequestBodySerializer(serializers.Serializer):
    new_title = serializers.CharField()
    new_content = serializers.CharField()
    reason = serializers.CharField()


class PageDeleteResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class PageDeleteRequestBodySerializer(serializers.Serializer):
    reason = serializers.CharField()


class TopicUpdateResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class TopicDeleteResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class TopicDeleteRequestBodySerializer(serializers.Serializer):
    reason = serializers.CharField()


class TopicCreateRequestBodySerializer(serializers.Serializer):
    note_id = serializers.IntegerField()
    title = serializers.CharField()
    reason = serializers.CharField(help_text="이슈의 reason에 대한 내용")


class PageHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PageHistory
        fields = "__all__"

    def create(self, validated_data):
        owner = validated_data.pop("owner")
        page = validated_data.pop("page")
        page_history = PageHistory.objects.create(owner=owner, page=page, **validated_data)
        return page_history


class PageCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    content = serializers.CharField(required=True)

    class Meta:
        model = Page
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        owner = validated_data["owners"][0]
        title = validated_data.pop("title")
        content = validated_data.pop("content")

        page = super().create(validated_data)
        page_history_data = {
            "owner": owner,
            "title": title,
            "content": content,
            "page": page,
            "version_type": PageVersionType.CURRENT,
        }
        page_history = PageHistory.objects.create(**page_history_data)
        return page_history


class PageDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = "__all__"

    def to_representation(self, page):
        version_no = self.context["version_no"]
        page_history = page.page_history.filter(page=page, version_no=version_no).first()
        if page_history is None:
            raise Http404("No PageHistory matches the given query.")
        owners = serializers.PrimaryKeyRelatedField(many=True, queryset=page.owners.all())
        issue = Issue.objects.filter(related_model_id=page_history.id, related_model_type=CtrlfContentType.PAGE).first()
        issue_id = issue.id if issue is not None else None

        return {
            "id": page.id,
            "topic": page.topic.id,
            "owners": owners.to_representation(page.owners.all()),
            "issue_id": issue_id,
            "title": page_history.title,
            "content": page_history.content,
            "is_approved": page_history.is_approved,
            "version_no": version_no,
            "version_type": page_history.version_type,
        }


class PageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        exclude = ["created_at", "updated_at"]

    def to_representation(self, page):
        page_history = page.page_history.filter(version_type=PageVersionType.CURRENT).first()
        owners = serializers.PrimaryKeyRelatedField(many=True, queryset=page.owners.all())

        return {
            "id": page.id,
            "owners": owners.to_representation(page.owners.all()),
            "topic": page.topic.id,
            "title": page_history.title,
            "version_no": page_history.version_no,
            "is_approved": page_history.is_approved,
        }


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


class IssueCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = "__all__"

    def create(self, validated_data):
        owner = validated_data.pop("owner")
        related_model = validated_data.pop("related_model")
        related_model_id = related_model.id
        validated_data["etc"] = related_model.title
        issue = Issue.objects.create(owner=owner, related_model_id=related_model_id, **validated_data)
        return issue


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
            page = PageHistory.objects.get(id=issue.related_model_id).page
            return Topic.objects.get(id=page.topic.id).id
        else:
            return None

    def get_note_id(self, issue):
        if issue.related_model_type == CtrlfContentType.NOTE:
            return issue.related_model_id
        elif issue.related_model_type == CtrlfContentType.TOPIC:
            topic = Topic.objects.get(id=issue.related_model_id)
        else:
            page = PageHistory.objects.get(id=issue.related_model_id).page
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


class IssueCountSerializer(serializers.Serializer):
    issues_count = serializers.IntegerField()
