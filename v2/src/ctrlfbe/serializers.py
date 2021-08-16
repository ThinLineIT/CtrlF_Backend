from rest_framework import serializers

from .models import Note, Page, Topic


class NoteListSerializer(serializers.ListSerializer):
    pass


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
        list_serializer_class = NoteListSerializer


class NoteListQuerySerializer(serializers.Serializer):
    cursor = serializers.IntegerField()


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ["id", "title", "created_at", "is_approved", "owners"]
        read_only_fields = ["id", "created_at"]


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
