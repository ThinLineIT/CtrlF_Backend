from django.db.models import fields
from rest_framework import serializers

from cs_wiki.models import Note, Page, Issue


class NoteSerializer(serializers.ModelSerializer):
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


class IssueListViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ("id", "title", "registration_date")


class DetailPageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ("id", "title", "content")
