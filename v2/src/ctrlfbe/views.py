from typing import List

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import ERR_NOTE_NOT_FOUND, ERR_TOPIC_NOT_FOUND
from .models import Note, Page, Topic
from .serializers import NoteSerializer, PageSerializer, TopicSerializer


class NoteDetailUpdateDeleteView(APIView):
    authentication_classes: List[str] = []

    @swagger_auto_schema(
        responses={200: NoteSerializer()},
        operation_summary="Note Detail API",
        operation_description="note_id에 해당하는 Note의 상세 내용을 리턴합니다",
    )
    def get(self, request, note_id):
        try:
            note = Note.objects.get(pk=note_id)
        except Note.DoesNotExist:
            return Response({"message": ERR_NOTE_NOT_FOUND}, status.HTTP_404_NOT_FOUND)

        serializer = NoteSerializer(note)
        return Response(serializer.data, status.HTTP_200_OK)


class TopicListView(APIView):
    authentication_classes: List[str] = []

    @swagger_auto_schema(
        responses={200: TopicSerializer(many=True)},
        operation_summary="Topic List API",
        operation_description="note_id에 해당하는 topic들의 list를 리턴해줍니다",
    )
    def get(self, request, note_id):
        try:
            Note.objects.get(pk=note_id)
        except Note.DoesNotExist:
            return Response({"message": ERR_NOTE_NOT_FOUND}, status.HTTP_404_NOT_FOUND)

        topics = Topic.objects.filter(note=note_id)

        serializer = TopicSerializer(topics, many=True)
        return Response(serializer.data, status.HTTP_200_OK)


class PageListView(APIView):
    authentication_classes: List[str] = []

    @swagger_auto_schema(
        responses={200: PageSerializer(many=True)},
        operation_summary="Page List API",
        operation_description="topic_id에 해당하는 page들의 list를 리턴해줍니다",
    )
    def get(self, request, topic_id):
        try:
            Topic.objects.get(pk=topic_id)
        except Topic.DoesNotExist:
            return Response({"message": ERR_TOPIC_NOT_FOUND}, status.HTTP_404_NOT_FOUND)

        pages = Page.objects.filter(topic=topic_id)

        serializer = PageSerializer(pages, many=True)
        return Response(serializer.data, status.HTTP_200_OK)
