from rest_framework import serializers

from .models import Note, Topic


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "title", "created_at", "is_approved", "owners"]
        read_only_fields = ["id", "created_at"]


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ["id", "title", "created_at", "is_approved", "owners"]
        read_only_fields = ["id", "created_at"]
