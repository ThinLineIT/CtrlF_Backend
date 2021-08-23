from typing import List, Optional

from ctrlf_auth.authentication import CtrlfAuthentication
from ctrlfbe.swagger import (
    SWAGGER_NOTE_DETAIL_VIEW,
    SWAGGER_NOTE_LIST_VIEW,
    SWAGGER_PAGE_LIST_VIEW,
    SWAGGER_TOPIC_LIST_VIEW,
)
from django.db.models import Model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import ERR_NOT_FOUND_MSG_MAP, ERR_UNEXPECTED, MAX_PRINTABLE_NOTE_COUNT
from .models import (
    CtrlfActionType,
    CtrlfContentType,
    CtrlfIssueStatus,
    Note,
    Page,
    Topic,
)
from .serializers import (
    ContentRequestSerializer,
    IssueCreateSerializer,
    NoteSerializer,
    OwnerSerializer,
    PageSerializer,
    TopicSerializer,
)


class BaseContentView(APIView):
    authentication_classes: List[str] = []
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


class NoteListView(APIView):
    authentication_classes = [
        CtrlfAuthentication,
    ]

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

    @swagger_auto_schema(query_serializer=NoteSerializer)
    def post(self, request, *args, **kwargs):
        user_serializer = OwnerSerializer(request.user)
        note_data = {"title": request.data.get("title"), "owners": [user_serializer.data]}
        note_serializer = NoteSerializer(data=note_data)

        if note_serializer.is_valid():
            note_serializer.save()

        content_request_data = {
            "user": user_serializer.data,
            "sub_id": 1,
            "type": CtrlfContentType.NOTE,
            "reason": "create",
            "action": CtrlfActionType.CREATE,
        }
        content_request_serializer = ContentRequestSerializer(data=content_request_data)
        if content_request_serializer.is_valid():
            content_request_serializer.save()

        issue_data = {
            "title": request.data.get("title"),
            "content": request.data.get("content"),
            "owner": user_serializer.data,
            "status": CtrlfIssueStatus.REQUESTED,
            "content_request": content_request_serializer.data,
        }
        issue_serializer = IssueCreateSerializer(data=issue_data)
        if issue_serializer.is_valid():
            issue_serializer.save()

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


class PageListView(BaseContentView):
    parent_model = Topic
    child_model = Page
    serializer = PageSerializer
    many = True

    @swagger_auto_schema(**SWAGGER_PAGE_LIST_VIEW)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
