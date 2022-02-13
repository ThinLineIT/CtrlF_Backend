from common.s3.client import S3Client
from ctrlfbe.mixins import CtrlfAuthenticationMixin
from ctrlfbe.swagger import (
    SWAGGER_HEALTH_CHECK_VIEW,
    SWAGGER_IMAGE_UPLOAD_VIEW,
    SWAGGER_ISSUE_APPROVE_VIEW,
    SWAGGER_ISSUE_COUNT,
    SWAGGER_ISSUE_DETAIL_VIEW,
    SWAGGER_ISSUE_LIST_VIEW,
    SWAGGER_NOTE_CREATE_VIEW,
    SWAGGER_NOTE_DETAIL_VIEW,
    SWAGGER_NOTE_LIST_VIEW,
    SWAGGER_NOTE_UPDATE_VIEW,
    SWAGGER_PAGE_CREATE_VIEW,
    SWAGGER_PAGE_DETAIL_VIEW,
    SWAGGER_PAGE_LIST_VIEW,
    SWAGGER_PAGE_UPDATE_VIEW,
    SWAGGER_TOPIC_CREATE_VIEW,
    SWAGGER_TOPIC_DETAIL_VIEW,
    SWAGGER_TOPIC_LIST_VIEW,
    SWAGGER_TOPIC_UPDATE_VIEW,
)
from django.conf import settings
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .basedata import NoteData, PageData, TopicData
from .models import CtrlfActionType, CtrlfIssueStatus, Issue, Note, Page, Topic
from .paginations import IssueListPagination, NoteListPagination
from .serializers import (
    IssueCountSerializer,
    IssueCreateSerializer,
    IssueDetailSerializer,
    IssueListSerializer,
    NoteSerializer,
    PageCreateSerializer,
    PageDetailSerializer,
    PageHistorySerializer,
    PageListSerializer,
    TopicSerializer,
)

s3_client = S3Client()


class BaseContentViewSet(CtrlfAuthenticationMixin, ModelViewSet):
    def paginated_list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        parent_model_kwargs = self.get_parent_kwargs(list(kwargs.values())[0])
        self.queryset = self.child_model.objects.filter(**parent_model_kwargs)

        return super().list(request, *args, **kwargs)

    def get_parent_kwargs(self, parent_id):
        parent_name = str(self.parent_model._meta).split(".")[1]
        parent_queryset = self.parent_model.objects.filter(id=parent_id)
        parent = get_object_or_404(parent_queryset)

        return {parent_name: parent}

    def create(self, request, *args, **data):
        ctrlf_user = self._ctrlf_authentication(request)
        model_data, issue_data = self.append_ctrlf_user(data, ctrlf_user)

        related_model_serializer = self.get_serializer(data=model_data)
        issue_serializer = IssueCreateSerializer(data=issue_data)

        related_model_serializer.is_valid(raise_exception=True)
        issue_serializer.is_valid(raise_exception=True)
        issue_serializer.save(related_model=related_model_serializer.save())

        return Response(status=status.HTTP_201_CREATED)

    def update(self, request, *args, **issue_data):
        ctrlf_user = self._ctrlf_authentication(request)
        issue_data["owner"] = ctrlf_user.id

        issue_serializer = IssueCreateSerializer(data=issue_data)
        issue_serializer.is_valid(raise_exception=True)
        issue_serializer.save(related_model=self.get_object())

        return Response(data={"message": "Note 수정 이슈를 생성하였습니다."}, status=status.HTTP_200_OK)

    def append_ctrlf_user(self, data, ctrlf_user):
        if self.serializer_class is PageHistorySerializer:
            data["model_data"]["owner"] = ctrlf_user.id
        else:
            data["model_data"]["owners"] = [ctrlf_user.id]
        data["issue_data"]["owner"] = ctrlf_user.id
        return data["model_data"], data["issue_data"]


class NoteViewSet(BaseContentViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    pagination_class = NoteListPagination
    lookup_url_kwarg = "note_id"

    @swagger_auto_schema(**SWAGGER_NOTE_LIST_VIEW)
    def list(self, request, *args, **kwargs):
        return super().paginated_list(request, *args, **kwargs)

    @swagger_auto_schema(**SWAGGER_NOTE_CREATE_VIEW)
    def create(self, request, *args, **kwargs):
        data = NoteData(request).build_create_data()
        return super().create(request, **data)

    @swagger_auto_schema(**SWAGGER_NOTE_DETAIL_VIEW)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(**SWAGGER_NOTE_UPDATE_VIEW)
    def update(self, request, *args, **kwargs):
        data = NoteData(request).build_update_data()
        return super().update(request, **data)


class TopicViewSet(BaseContentViewSet):
    parent_model = Note
    child_model = Topic
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    lookup_url_kwarg = "topic_id"

    @swagger_auto_schema(**SWAGGER_TOPIC_LIST_VIEW)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(**SWAGGER_TOPIC_CREATE_VIEW)
    def create(self, request, *args, **kwargs):
        data = TopicData(request).build_create_data()
        return super().create(request, **data)

    @swagger_auto_schema(**SWAGGER_TOPIC_DETAIL_VIEW)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(**SWAGGER_TOPIC_UPDATE_VIEW)
    def update(self, request, *args, **kwargs):
        data = TopicData(request).build_update_data()
        return super().update(request, **data)


class PageViewSet(BaseContentViewSet):
    parent_model = Topic
    child_model = Page
    queryset = Page.objects.all()
    lookup_url_kwarg = "page_id"
    serializer_class = PageCreateSerializer

    @swagger_auto_schema(**SWAGGER_PAGE_LIST_VIEW)
    def list(self, request, *args, **kwargs):
        self.serializer_class = PageListSerializer
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(**SWAGGER_PAGE_CREATE_VIEW)
    def create(self, request, *args, **kwargs):
        data = PageData(request).build_create_data()
        return super().create(request, **data)

    @swagger_auto_schema(**SWAGGER_PAGE_DETAIL_VIEW)
    def retrieve(self, request, *args, **kwargs):
        page_serializer = PageDetailSerializer(self.get_object(), context=kwargs)
        return Response(data=page_serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(**SWAGGER_PAGE_UPDATE_VIEW)
    def update(self, request, *args, **kwargs):
        self.serializer_class = PageHistorySerializer
        data = PageData(request).build_update_data(self.get_object())
        return super().create(request, **data)


class IssueViewSet(CtrlfAuthenticationMixin, ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueListSerializer
    pagination_class = IssueListPagination
    lookup_url_kwarg = "issue_id"

    @swagger_auto_schema(**SWAGGER_ISSUE_LIST_VIEW)
    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(Q(status=CtrlfIssueStatus.REQUESTED) | Q(status=CtrlfIssueStatus.REJECTED))
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(**SWAGGER_ISSUE_DETAIL_VIEW)
    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = IssueDetailSerializer
        return super().retrieve(request, *args, **kwargs)


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
            ctrlf_content = self.get_ctrlf_content(issue=issue, ctrlf_user=issue_approve_request_user)
        except ValueError:
            return Response(data={"message": "승인 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        if not ctrlf_content.owners.filter(email=issue_approve_request_user.email).exists():
            return Response(status=status.HTTP_403_FORBIDDEN)

        if issue.action == CtrlfActionType.UPDATE:
            is_page = ctrlf_content.__class__ is Page
            ctrlf_content.process_update() if is_page else ctrlf_content.process_update(issue.title)
        elif issue.action == CtrlfActionType.CREATE:
            ctrlf_content.process_create()

        issue.status = CtrlfIssueStatus.APPROVED
        issue.save()

        return Response(data={"message": "승인 완료"}, status=status.HTTP_200_OK)

    def get_ctrlf_content(self, issue, ctrlf_user):
        ctrlf_content = issue.get_ctrlf_content()
        if issue.action == CtrlfActionType.CREATE:
            self.validate_exists_owner(ctrlf_content, ctrlf_user)
        return ctrlf_content

    def validate_exists_owner(self, content, ctrlf_user):
        owner_id = ctrlf_user.id
        exists_owner_method_map = {Page: "exists_topic_owner", Topic: "exists_note_owner", Note: "exists_owner"}[
            content.__class__
        ]
        if not getattr(content, exists_owner_method_map)(owner_id):
            raise ValueError


class ImageUploadView(APIView):
    BUCKET_BASE_DIR = settings.S3_BUCKET_BASE_DIR
    BASE_URL = settings.S3_BASE_URL
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(**SWAGGER_IMAGE_UPLOAD_VIEW)
    def post(self, request, *args, **kwargs):
        image_data = request.FILES["image"]
        file_name_to_upload = image_data.name
        file_content_type = image_data.content_type
        bucket_path = f"{self.BUCKET_BASE_DIR}/{file_name_to_upload}"
        s3_client.upload_file_object(image_data=image_data, bucket_path=bucket_path, content_type=file_content_type)

        return Response(data={"image_url": f"{self.BASE_URL}/{bucket_path}"}, status=status.HTTP_200_OK)


class IssueCount(APIView):
    @swagger_auto_schema(**SWAGGER_ISSUE_COUNT)
    def get(self, request):
        serializer = IssueCountSerializer({"issues_count": Issue.objects.count()})
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class HealthCheckView(APIView):
    @swagger_auto_schema(**SWAGGER_HEALTH_CHECK_VIEW)
    def get(self, request):
        return Response(data={"message": "OK"}, status=status.HTTP_200_OK)
