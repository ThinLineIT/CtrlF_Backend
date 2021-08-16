from typing import List, Optional

from ctrlfbe.serializers import NoteListQuerySerializer
from django.db.models import Model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import ERR_NOTE_NOT_FOUND, ERR_TOPIC_NOT_FOUND, MAX_PRINTABLE_NOTE_COUNT
from .models import Note, Page, Topic
from .serializers import NoteSerializer, PageSerializer, TopicSerializer


class BaseContentView(APIView):
    authentication_classes: List[str] = []
    child_model: Optional[Model] = None
    many = False

    def get(self, request, *args, **kwargs):
        id_from_path_param = list(kwargs.values())[0]
        result = self.model.objects.filter(id=id_from_path_param).first()

        if result is None:
            return Response(data={"message": self.error_msg}, status=status.HTTP_404_NOT_FOUND)

        if self.child_model:
            key_ = str(result._meta).split(".")[1]
            result = self.child_model.objects.filter(**{key_: result})
        if self.many:
            serializer = self.serializer(result, many=True)
        else:
            serializer = self.serializer(result)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class NoteAPIView(APIView):
    authentication_classes: List[str] = []

    @swagger_auto_schema(query_serializer=NoteListQuerySerializer)
    def get(self, request):
        current_cursor = int(request.query_params["cursor"])
        notes = Note.objects.all()[current_cursor : current_cursor + MAX_PRINTABLE_NOTE_COUNT]
        serializer = NoteSerializer(notes, many=True)
        serialized_notes = serializer.data
        return Response(
            data={"next_cursor": current_cursor + len(serialized_notes), "notes": serialized_notes},
            status=status.HTTP_200_OK,
        )


class NoteDetailUpdateDeleteView(BaseContentView):
    model = Note
    serializer = NoteSerializer
    error_msg = ERR_NOTE_NOT_FOUND

    @swagger_auto_schema(
        responses={200: NoteSerializer()},
        operation_summary="Note Detail API",
        operation_description="note_id에 해당하는 Note의 상세 내용을 리턴합니다",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TopicListView(BaseContentView):
    model = Note
    child_model = Topic
    serializer = TopicSerializer
    many = True
    error_msg = ERR_NOTE_NOT_FOUND

    @swagger_auto_schema(
        responses={200: TopicSerializer(many=True)},
        operation_summary="Topic List API",
        operation_description="note_id에 해당하는 topic들의 list를 리턴해줍니다",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PageListView(BaseContentView):
    model = Topic
    child_model = Page
    serializer = PageSerializer
    many = True
    error_msg = ERR_TOPIC_NOT_FOUND

    @swagger_auto_schema(
        responses={200: PageSerializer(many=True)},
        operation_summary="Page List API",
        operation_description="topic_id에 해당하는 page들의 list를 리턴해줍니다",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
