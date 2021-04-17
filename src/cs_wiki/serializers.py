from django.db.models import fields
from rest_framework import serializers

from cs_wiki.models import Note, Topic, Page, Issue


class NoteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ("id", "title")

    def create(self, validated_data):
        return Note.objects.create(**validated_data)


class AllPageCountViewSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ("count",)

    def get_count(self, obj):
        return obj


class DetailPageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ("id", "title", "content")


class PageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ("id", "title", "content", "topic_id")

    def create(self, validated_data):
        return Page.objects.create(**validated_data)


class TopicDetailViewSerializer(serializers.ModelSerializer):
    page = PageListSerializer()

    class Meta:
        model = Topic
        fields = ("id", "title", "note_id", "page")


class NoteDetailViewSerializer(serializers.ModelSerializer):
    topic = TopicDetailViewSerializer()

    class Meta:
        model = Note
        fields = ("id", "title", "topic")

    def to_representation(self, instance):
        note_result = {}
        note_result["id"] = instance.id
        note_result["title"] = instance.title
        note_result["topics"] = []

        for topic in instance.topic_set.all():
            temp_topic = {}
            temp_topic["id"] = topic.id
            temp_topic["title"] = topic.title
            temp_topic["pages"] = []
            for page in topic.page_set.all():
                temp_page = {}
                temp_page["id"] = page.id
                temp_page["title"] = page.title
                temp_topic["pages"].append(temp_page)
            note_result["topics"].append(temp_topic)
        return note_result


class IssueListViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ("id", "title", "content", "registration_date")

    def create(self, validated_data):
        return Issue.objects.create(**validated_data)


class TopicListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ("id", "title", "note_id")

    def create(self, validated_data):
        result = Topic.objects.create(**validated_data)
        print(result)
        return result
