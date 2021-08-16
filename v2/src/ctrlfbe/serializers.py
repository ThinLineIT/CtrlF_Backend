from ctrlfbe.models import Note
from rest_framework import serializers


class NoteListSerializer(serializers.ListSerializer):
    pass


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"
        list_serializer_class = NoteListSerializer
