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


class TopicCreateRequestBodySerializer(serializers.Serializer):
    note_id = serializers.IntegerField()
    title = serializers.CharField()
    reason = serializers.CharField(help_text="이슈의 reason에 대한 내용")


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
        issue = Issue.objects.filter(related_model_id=obj.id, related_model_type=CtrlfContentType.PAGE).first()
        if issue is None:
            return issue
        else:
            return issue.id


class PageCreateRequestBodySerializer(serializers.Serializer):
    topic_id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()
    reason = serializers.CharField(help_text="이슈의 reason에 대한 내용")


class IssueSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    owner = serializers.EmailField()
    title = serializers.CharField()
    reason = serializers.CharField()
    status = serializers.CharField()
    related_model_type = serializers.CharField()
    related_model_id = serializers.IntegerField()
    action = serializers.CharField()


class IssueDetailSerializer(serializers.Serializer):
    note_id = serializers.SerializerMethodField()
    topic_id = serializers.SerializerMethodField()
    page_id = serializers.SerializerMethodField()

    id = serializers.IntegerField()
    owner = serializers.EmailField()
    title = serializers.CharField()
    reason = serializers.CharField()
    status = serializers.CharField()
    related_model_type = serializers.CharField()
    related_model_id = serializers.IntegerField()
    action = serializers.CharField()

    def get_page_id(self, issue):
        if issue.related_model_type == CtrlfContentType.PAGE:
            return issue.related_model_id
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


class IssueApproveResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class IssueApproveRequestBodySerializer(serializers.Serializer):
    issue_id = serializers.IntegerField()


class ImageUploadRequestBodySerializer(serializers.Serializer):
    img_data = serializers.ImageField()


class ImageSerializer(serializers.Serializer):
    img_url = serializers.CharField()
