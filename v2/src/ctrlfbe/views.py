from typing import Optional

from ctrlfbe.mixins import CtrlfAuthenticationMixin
from ctrlfbe.swagger import (
    SWAGGER_NOTE_CREATE_VIEW,
    SWAGGER_NOTE_DETAIL_VIEW,
    SWAGGER_NOTE_LIST_VIEW,
    SWAGGER_PAGE_DETAIL_VIEW,
    SWAGGER_PAGE_LIST_VIEW,
    SWAGGER_TOPIC_DETAIL_VIEW,
    SWAGGER_TOPIC_LIST_VIEW,
)
from django.db.models import Model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import ERR_NOT_FOUND_MSG_MAP, ERR_UNEXPECTED, MAX_PRINTABLE_NOTE_COUNT
from .models import CtrlfIssueStatus, Note, Page, Topic
from .serializers import (
    IssueCreateSerializer,
    NoteSerializer,
    PageSerializer,
    TopicSerializer,
)


class BaseContentView(APIView):
    child_model: Optional[Model] = None
    many = False

    def get(self, request, *args, **kwargs):
        id_from_path_param = list(kwargs.values())[0]
        result = self.parent_model.objects.filter(id=id_from_path_param).first()
        class_name_lower = str(self.parent_model._meta).split(".")[1]

        if result is None:
            return Response(
                data={"message": ERR_NOT_FOUND_MSG_MAP.get(class_name_lower, ERR_UNEXPECTED)},
                status=status.HTTP_404_NOT_FOUND,
            )

        if self.child_model:
            result = self.child_model.objects.filter(**{class_name_lower: result})
        if self.many:
            serializer = self.serializer(result, many=True)
        else:
            serializer = self.serializer(result)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class NoteListCreateView(CtrlfAuthenticationMixin, APIView):
    @swagger_auto_schema(**SWAGGER_NOTE_LIST_VIEW)
    def get(self, request):
        current_cursor = int(request.query_params["cursor"])
        notes = Note.objects.all()[current_cursor : current_cursor + MAX_PRINTABLE_NOTE_COUNT]
        serializer = NoteSerializer(notes, many=True)
        serialized_notes = serializer.data
        return Response(
            data={"next_cursor": current_cursor + len(serialized_notes), "notes": serialized_notes},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(**SWAGGER_NOTE_CREATE_VIEW)
    def post(self, request, *args, **kwargs):
        ctrlf_user = self._ctrlf_authentication(request)
        note_data = {
            "title": request.data["title"],
            "owners": [ctrlf_user.id],
        }
        issue_data = {
            "title": request.data["title"],
            "content": request.data["content"],
            "owner": ctrlf_user.id,
            "status": CtrlfIssueStatus.REQUESTED,
        }
        note_serializer = NoteSerializer(data=note_data)
        issue_serializer = IssueCreateSerializer(data=issue_data)

        if note_serializer.is_valid() and issue_serializer.is_valid():
            issue_serializer.save(note=note_serializer.save())

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)


class NoteDetailUpdateDeleteView(BaseContentView):
    parent_model = Note
    serializer = NoteSerializer

    @swagger_auto_schema(**SWAGGER_NOTE_DETAIL_VIEW)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TopicListView(BaseContentView):
    parent_model = Note
    child_model = Topic
    serializer = TopicSerializer
    many = True

    @swagger_auto_schema(**SWAGGER_TOPIC_LIST_VIEW)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TopicDetailUpdateDeleteView(BaseContentView):
    parent_model = Topic
    serializer = TopicSerializer

    @swagger_auto_schema(**SWAGGER_TOPIC_DETAIL_VIEW)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        topic = Topic.objects.get(id=kwargs["topic_id"])
        topic.delete()
        return Response(data={"message": "삭제 되었습니다."}, status=status.HTTP_204_NO_CONTENT)


class PageListView(BaseContentView):
    parent_model = Topic
    child_model = Page
    serializer = PageSerializer
    many = True

    @swagger_auto_schema(**SWAGGER_PAGE_LIST_VIEW)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PageDetailUpdateDeleteView(BaseContentView):
    parent_model = Page
    serializer = PageSerializer

    @swagger_auto_schema(**SWAGGER_PAGE_DETAIL_VIEW)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
