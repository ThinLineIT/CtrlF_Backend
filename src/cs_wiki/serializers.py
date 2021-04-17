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
        fields = ("id", "title", "content")

    def create(self, validated_data):
        return Issue.objects.create(**validated_data)


class TopicDetailViewSerializer(serializers.ModelSerializer):
    pages = PageListSerializer(many=True)

    class Meta:
        model = Topic
        fields = ("id", "title", "pages")


class NoteDetailViewSerializer(serializers.ModelSerializer):
    topics = TopicDetailViewSerializer(many=True)

    class Meta:
        model = Note
        fields = ("id", "title", "topics")


class IssueListViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ("id", "title", "registration_date")

    def create(self, validated_data):
        return Issue.objects.create(**validated_data)


class TopicListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ("id", "title")

    def create(self, validated_data):
        return Issue.objects.create(**validated_data)
