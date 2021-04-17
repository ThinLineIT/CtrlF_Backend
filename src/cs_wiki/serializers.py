from rest_framework import serializers

from cs_wiki.models import Note, Page


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ("id", "title")


class AllPageCountViewSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ("count",)

    def get_count(self, obj):
        print("abcde: {}".format(obj))
        print(obj)
        return obj
