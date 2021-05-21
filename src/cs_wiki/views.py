from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response

from cs_wiki.models import Note, Page, Issue, Topic
from cs_wiki.serializers import (
    HomeSerializer,
    IssueListSerializer,
    NoteListSerializer,
    NoteDetailSerializer,
    PageSerializer,
    PageDetailSerializer,
    TopicSerializer,
)

from rest_framework import status


class HomeView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request):
        count = Page.objects.all().count()
        notes = Note.objects.all()
        issues = Issue.objects.order_by("-registration_date")[:6]

        home = {"count": count, "notes": notes, "issues": issues}

        serializer = HomeSerializer(home)
        return Response(serializer.data)


class IssueListView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request, *args, **kwargs):
        if "note_id" not in kwargs and "topic_id" in kwargs:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        issues = Issue.objects.order_by("-registration_date")

        if "limit" in kwargs:
            issues = issues[: int(kwargs["limit"])]

        if "note_id" in kwargs and "topic_id" in kwargs:
            issues = issues.filter(note_id=kwargs["note_id"]).filter(
                topic_id=kwargs["topic_id"]
            )
        elif "note_id" in kwargs and "topic_id" not in kwargs:
            issues = issues.filter(note_id=kwargs["note_id"])

        if "search" in kwargs:
            issues = issues.filter(title=kwargs["search"])

        serializer = IssueListSerializer(issues, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=IssueListSerializer)
    def post(self, request):
        topic = Topic.objects.get(id=request.data["topic_id"])
        note = Note.objects.get(id=request.data["note_id"])

        if str(topic.note_id) != str(note.title):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = IssueListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class NoteListView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request, *args, **kwargs):
        notes = Note.objects.all()

        if "search" in request.GET:
            notes = notes.filter(title=request.GET["search"])

        serializer = NoteListSerializer(notes, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=NoteListSerializer)
    def post(self, request):
        serializer = NoteListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class NoteDetailView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request, **kwargs):
        try:
            note_id = kwargs["note_id"]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            note = Note.objects.prefetch_related(
                "topic_set", "topic_set__page_set"
            ).get(id=note_id)
        except Note.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = NoteDetailSerializer(note)
        return Response(serializer.data)


class TopicView(APIView):
    @swagger_auto_schema(request_body=TopicSerializer)
    def post(self, request):
        serializer = TopicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class PageView(APIView):
    @swagger_auto_schema(request_body=PageSerializer)
    def post(self, request):
        topic = Topic.objects.get(id=request.data["topic_id"])
        note = Note.objects.get(id=request.data["note_id"])

        if str(topic.note_id) != str(note.title):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = PageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class PageDetailView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request, **kwargs):
        try:
            page_id = kwargs["page_id"]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PageDetailSerializer(page)
        return Response(serializer.data)
