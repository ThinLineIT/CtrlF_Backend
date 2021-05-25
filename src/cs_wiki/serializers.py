from django.db import models
from django.db.models import fields
from rest_framework import serializers

from cs_wiki.models import Note, Topic, Page, Issue


class PagesCountSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ("count",)

    def get_count(self, obj):
        return obj


class IssueListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ("id", "title", "note_id", "topic_id", "registration_date", "content")

    def create(self, validated_data):
        return Issue.objects.create(**validated_data)


class NoteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ("id", "title")

    def create(self, validated_data):
        return Note.objects.create(**validated_data)


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ("id", "note_id", "title")

    def create(self, validated_data):
        return Topic.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ("id", "topic_id", "title", "content")

    def create(self, validated_data):
        return Page.objects.create(**validated_data)


class PageDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ("id", "title", "content")


class HomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ("count", "notes", "issues")

    def to_representation(self, instance):
        home = {}

        home["count"] = instance["count"]

        home["notes"] = []
        for note in instance["notes"]:
            temp_note = {}
            temp_note["id"] = note.id
            temp_note["title"] = note.title
            home["notes"].append(temp_note)

        home["issues"] = []
        for issue in instance["issues"]:
            temp_issue = {}
            temp_issue["id"] = issue.id
            temp_issue["title"] = issue.title
            temp_issue["note_id"] = issue.note_id.id
            temp_issue["topic_id"] = issue.topic_id.id
            home["issues"].append(temp_issue)

        return home


class TopicDetailViewSerializer(serializers.ModelSerializer):
    page = PageSerializer()

    class Meta:
        model = Topic
        fields = ("id", "title", "note_id", "page")


class NoteDetailSerializer(serializers.ModelSerializer):
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
