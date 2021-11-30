from ctrlfbe.mixins import CtrlfAuthenticationMixin
from ctrlfbe.swagger import (
    SWAGGER_HEALTH_CHECK_VIEW,
    SWAGGER_ISSUE_APPROVE_VIEW,
    SWAGGER_ISSUE_DETAIL_VIEW,
    SWAGGER_ISSUE_LIST_VIEW,
    SWAGGER_NOTE_CREATE_VIEW,
    SWAGGER_NOTE_DETAIL_VIEW,
    SWAGGER_NOTE_LIST_VIEW,
    SWAGGER_PAGE_CREATE_VIEW,
    SWAGGER_PAGE_DETAIL_VIEW,
    SWAGGER_PAGE_LIST_VIEW,
    SWAGGER_TOPIC_CREATE_VIEW,
    SWAGGER_TOPIC_DETAIL_VIEW,
    SWAGGER_TOPIC_LIST_VIEW,
)
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .basedata import NoteData, PageData, TopicData
from .constants import ERR_NOT_FOUND_MSG_MAP, ERR_UNEXPECTED
from .models import (
    CtrlfActionType,
    CtrlfContentType,
    CtrlfIssueStatus,
    Issue,
    Note,
    Page,
    Topic,
)
from .paginations import IssueListPagination, NoteListPagination
from .serializers import (
    IssueCreateSerializer,
    IssueDetailSerializer,
    IssueSerializer,
    NoteSerializer,
    NoteUpdateRequestBodySerializer,
    PageListSerializer,
    PageSerializer,
    TopicSerializer,
)


class NoteViewSet(CtrlfAuthenticationMixin, ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    pagination_class = NoteListPagination
    lookup_url_kwarg = "note_id"

    @swagger_auto_schema(**SWAGGER_NOTE_LIST_VIEW)
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)

    @swagger_auto_schema(**SWAGGER_NOTE_CREATE_VIEW)
    def create(self, request, *args, **kwargs):
        ctrlf_user = self._ctrlf_authentication(request)
        note_data, issue_data = NoteData().build_data(request, ctrlf_user)

        note_serializer = NoteSerializer(data=note_data)
        issue_serializer = IssueCreateSerializer(data=issue_data)

        if note_serializer.is_valid() and issue_serializer.is_valid():
            issue_serializer.save(related_model=note_serializer.save())
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(**SWAGGER_NOTE_DETAIL_VIEW)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        ctrlf_user = self._ctrlf_authentication(request)
        note_id = kwargs["note_id"]
        note = Note.objects.filter(id=note_id).first()
        if note is None:
            return Response(data={"message": "Note를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        note_serializer = NoteUpdateRequestBodySerializer(data=request.data)
        if not note_serializer.is_valid():
            return Response(data={"message": "요청이 올바르지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        issue_data = {
            "owner": ctrlf_user.id,
            "title": request.data["new_title"],
            "reason": request.data["reason"],
            "status": CtrlfIssueStatus.REQUESTED,
            "related_model_type": CtrlfContentType.NOTE,
            "action": CtrlfActionType.UPDATE,
            "etc": note.title,
        }
        issue_serializer = IssueCreateSerializer(data=issue_data)
        issue_serializer.is_valid(raise_exception=True)
        issue_serializer.save(related_model=note)

        return Response(data={"message": "Note 수정 이슈를 생성하였습니다."}, status=status.HTTP_200_OK)


class TopicViewSet(CtrlfAuthenticationMixin, ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    lookup_url_kwarg = "topic_id"

    @swagger_auto_schema(**SWAGGER_TOPIC_LIST_VIEW)
    def list(self, request, *args, **kwargs):
        note_id = list(kwargs.values())[0]
        note = Note.objects.filter(id=note_id).first()
        if note is None:
            return Response(
                data={"message": ERR_NOT_FOUND_MSG_MAP.get("note", ERR_UNEXPECTED)},
                status=status.HTTP_404_NOT_FOUND,
            )

        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(**SWAGGER_TOPIC_CREATE_VIEW)
    def create(self, request, *args, **kwargs):
        ctrlf_user = self._ctrlf_authentication(request)
        topic_data, issue_data = TopicData().build_data(request, ctrlf_user)

        topic_serializer = TopicSerializer(data=topic_data)
        issue_serializer = IssueCreateSerializer(data=issue_data)

        if topic_serializer.is_valid() and issue_serializer.is_valid():
            issue_serializer.save(related_model=topic_serializer.save())
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(**SWAGGER_TOPIC_DETAIL_VIEW)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(self, request, *args, **kwargs)


class PageViewSet(CtrlfAuthenticationMixin, ModelViewSet):
    queryset = Page.objects.all()
    lookup_url_kwarg = "page_id"
    serializer_class = PageSerializer

    @swagger_auto_schema(**SWAGGER_PAGE_LIST_VIEW)
    def list(self, request, *args, **kwargs):
        self.serializer_class = PageListSerializer
        topic_id = list(kwargs.values())[0]
        topic = Topic.objects.filter(id=topic_id).first()
        if topic is None:
            return Response(
                data={"message": ERR_NOT_FOUND_MSG_MAP.get("topic", ERR_UNEXPECTED)},
                status=status.HTTP_404_NOT_FOUND,
            )
        return super().list(self, request, *args, **kwargs)

    @swagger_auto_schema(**SWAGGER_PAGE_CREATE_VIEW)
    def create(self, request, *args, **kwargs):
        ctrlf_user = self._ctrlf_authentication(request)
        page_data, issue_data = PageData().build_data(request, ctrlf_user)

        page_serializer = PageSerializer(data=page_data)
        issue_serializer = IssueCreateSerializer(data=issue_data)

        if page_serializer.is_valid() and issue_serializer.is_valid():
            issue_serializer.save(related_model=page_serializer.save())
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(**SWAGGER_PAGE_DETAIL_VIEW)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(self, request, *args, **kwargs)


class IssueViewSet(CtrlfAuthenticationMixin, ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    pagination_class = IssueListPagination
    lookup_url_kwarg = "issue_id"

    @swagger_auto_schema(**SWAGGER_ISSUE_LIST_VIEW)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(**SWAGGER_ISSUE_DETAIL_VIEW)
    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = IssueDetailSerializer
        return super().retrieve(self, request, *args, **kwargs)


class IssueApproveView(CtrlfAuthenticationMixin, APIView):
    @swagger_auto_schema(**SWAGGER_ISSUE_APPROVE_VIEW)
    def post(self, request, *args, **kwargs):
        ctrlf_user = self._ctrlf_authentication(request)
        issue_id = request.data["issue_id"]
        try:
            issue = Issue.objects.get(id=issue_id)
        except Issue.DoesNotExist:
            return Response(data={"message": "이슈 ID를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        try:
            ctrlf_content = self.get_content(issue=issue, ctrlf_user=ctrlf_user)
        except ValueError:
            return Response(data={"message": "승인 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        if issue.action == CtrlfActionType.UPDATE:
            if isinstance(ctrlf_content, Note):
                ctrlf_content.title = issue.title

        ctrlf_content.is_approved = True
        ctrlf_content.save()
        issue.status = CtrlfIssueStatus.APPROVED
        issue.save()

        return Response(data={"message": "승인 완료"}, status=status.HTTP_200_OK)

    def get_content(self, issue, ctrlf_user):
        content = (
            Page.objects.get(id=issue.related_model_id)
            if issue.related_model_type == CtrlfContentType.PAGE
            else Note.objects.get(id=issue.related_model_id)
            if issue.related_model_type == CtrlfContentType.NOTE
            else Topic.objects.get(id=issue.related_model_id)
            if issue.related_model_type == CtrlfContentType.TOPIC
            else None
        )
        if type(content) is Page:
            if not content.topic.owners.filter(id=ctrlf_user.id).exists():
                raise ValueError
        elif type(content) is Topic:
            if not content.note.owners.filter(id=ctrlf_user.id).exists():
                raise ValueError
        elif type(content) is Note:
            if not content.owners.filter(id=ctrlf_user.id).exists():
                raise ValueError

        return content


class HealthCheckView(APIView):
    @swagger_auto_schema(**SWAGGER_HEALTH_CHECK_VIEW)
    def get(self, request):
        return Response(data={"message": "OK"}, status=status.HTTP_200_OK)
