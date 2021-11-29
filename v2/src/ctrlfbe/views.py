from typing import Optional

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
    SWAGGER_TOPIC_UPDATE_VIEW,
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
    Issue,
    Note,
    Page,
    Topic,
)
from .serializers import (
    IssueCreateSerializer,
    IssueDetailSerializer,
    IssueSerializer,
    NoteSerializer,
    PageListSerializer,
    PageSerializer,
    TopicSerializer,
    TopicUpdateRequestBodySerializer,
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
            "owner": ctrlf_user.id,
            "title": request.data["title"],
            "reason": request.data["reason"],
            "status": CtrlfIssueStatus.REQUESTED,
            "related_model_type": CtrlfContentType.NOTE,
            "action": CtrlfActionType.CREATE,
        }
        note_serializer = NoteSerializer(data=note_data)
        issue_serializer = IssueCreateSerializer(data=issue_data)

        if note_serializer.is_valid() and issue_serializer.is_valid():
            issue_serializer.save(related_model=note_serializer.save())
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


class TopicCreateView(CtrlfAuthenticationMixin, APIView):
    @swagger_auto_schema(**SWAGGER_TOPIC_CREATE_VIEW)
    def post(self, request, *args, **kwargs):
        ctrlf_user = self._ctrlf_authentication(request)
        topic_data = {
            "note": request.data["note_id"],
            "title": request.data["title"],
            "owners": [ctrlf_user.id],
        }
        issue_data = {
            "owner": ctrlf_user.id,
            "title": request.data["title"],
            "reason": request.data["reason"],
            "status": CtrlfIssueStatus.REQUESTED,
            "related_model_type": CtrlfContentType.TOPIC,
            "action": CtrlfActionType.CREATE,
        }
        topic_serializer = TopicSerializer(data=topic_data)
        issue_serializer = IssueCreateSerializer(data=issue_data)
        if topic_serializer.is_valid() and issue_serializer.is_valid():
            issue_serializer.save(related_model=topic_serializer.save())
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)


class TopicDetailUpdateDeleteView(CtrlfAuthenticationMixin, BaseContentView):
    parent_model = Topic
    serializer = TopicSerializer

    @swagger_auto_schema(**SWAGGER_TOPIC_DETAIL_VIEW)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(**SWAGGER_TOPIC_UPDATE_VIEW)
    def post(self, request, *args, **kwargs):
        ctrlf_user = self._ctrlf_authentication(request)
        topic = Topic.objects.filter(id=kwargs["topic_id"]).first()
        if topic is None:
            return Response(data={"message": "Topic이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        topic_serializer = TopicUpdateRequestBodySerializer(data=request.data)
        if not topic_serializer.is_valid():
            return Response(data={"message": "요청이 유효하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        issue_data = {
            "owner": ctrlf_user.id,
            "title": request.data["new_title"],
            "reason": request.data["reason"],
            "status": CtrlfIssueStatus.REQUESTED,
            "related_model_type": CtrlfContentType.TOPIC,
            "action": CtrlfActionType.UPDATE,
            "etc": topic.title,
        }
        issue_serializer = IssueCreateSerializer(data=issue_data)
        issue_serializer.is_valid(raise_exception=True)
        issue_serializer.save(related_model=topic)

        return Response(data={"message": "Topic 수정 이슈를 생성하였습니다."}, status=status.HTTP_200_OK)


class PageListView(BaseContentView):
    parent_model = Topic
    child_model = Page
    serializer = PageListSerializer
    many = True

    @swagger_auto_schema(**SWAGGER_PAGE_LIST_VIEW)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PageCreateView(CtrlfAuthenticationMixin, APIView):
    @swagger_auto_schema(**SWAGGER_PAGE_CREATE_VIEW)
    def post(self, request, *args, **kwargs):
        ctrlf_user = self._ctrlf_authentication(request)
        page_data = {
            "topic": request.data["topic_id"],
            "title": request.data["title"],
            "content": request.data["content"],
            "owners": [ctrlf_user.id],
        }
        issue_data = {
            "owner": ctrlf_user.id,
            "title": request.data["title"],
            "reason": request.data["reason"],
            "status": CtrlfIssueStatus.REQUESTED,
            "related_model_type": CtrlfContentType.PAGE,
            "action": CtrlfActionType.CREATE,
        }
        page_serializer = PageSerializer(data=page_data)
        issue_serializer = IssueCreateSerializer(data=issue_data)

        if page_serializer.is_valid() and issue_serializer.is_valid():
            issue_serializer.save(related_model=page_serializer.save())
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)


class PageDetailUpdateDeleteView(BaseContentView):
    parent_model = Page
    serializer = PageSerializer

    @swagger_auto_schema(**SWAGGER_PAGE_DETAIL_VIEW)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class IssueListView(APIView):
    @swagger_auto_schema(**SWAGGER_ISSUE_LIST_VIEW)
    def get(self, request, *args, **kwargs):
        current_cursor = int(request.query_params["cursor"])
        issues = Issue.objects.all()[current_cursor : current_cursor + MAX_PRINTABLE_NOTE_COUNT]
        serializer = IssueSerializer(issues, many=True)
        serialized_issues = serializer.data

        return Response(
            data={"next_cursor": current_cursor + len(serialized_issues), "issues": serialized_issues},
            status=status.HTTP_200_OK,
        )


class IssueDetailView(APIView):
    @swagger_auto_schema(**SWAGGER_ISSUE_DETAIL_VIEW)
    def get(self, request, issue_id):
        try:
            issues = Issue.objects.get(id=issue_id)
        except Issue.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = IssueDetailSerializer(issues)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class IssueApproveView(CtrlfAuthenticationMixin, APIView):
    @swagger_auto_schema(**SWAGGER_ISSUE_APPROVE_VIEW)
    def post(self, request, *args, **kwargs):
        issue_approve_request_user = self._ctrlf_authentication(request)
        issue_id = request.data["issue_id"]
        try:
            issue = Issue.objects.get(id=issue_id)
        except Issue.DoesNotExist:
            return Response(data={"message": "이슈 ID를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        try:
            ctrlf_content = self.get_content(issue=issue, ctrlf_user=issue_approve_request_user)
        except ValueError:
            return Response(data={"message": "승인 권한이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        if issue.action == CtrlfActionType.UPDATE:
            if not ctrlf_content.owners.filter(email=issue_approve_request_user.email).exists():
                return Response(status=status.HTTP_403_FORBIDDEN)
            if isinstance(ctrlf_content, Topic):
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
        if issue.action == CtrlfActionType.CREATE:
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
