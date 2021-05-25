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
    PagesCountSerializer,
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


class PagesCountView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request):
        count = Page.objects.all().count()

        serializer = PagesCountSerializer(count)
        return Response(serializer.data)


class IssueListView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request):
        if "note_id" not in request.GET and "topic_id" in request.GET:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        issues = Issue.objects.order_by("-registration_date")

        if "note_id" in request.GET and "topic_id" in request.GET:
            issues = issues.filter(note_id=request.GET["note_id"]).filter(
                topic_id=request.GET["topic_id"]
            )
        elif "note_id" in request.GET and "topic_id" not in request.GET:
            issues = issues.filter(note_id=request.GET["note_id"])

        if "search" in request.GET and request.GET["search"] != "":
            issues = issues.filter(title__contains=request.GET["search"])

        if "limit" in request.GET:
            issues = issues[: int(request.GET["limit"])]

        serializer = IssueListSerializer(issues, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=IssueListSerializer)
    def post(self, request):
        serializer = IssueListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class IssueDetailView(APIView):
    @swagger_auto_schema(request_body=IssueListSerializer)
    def patch(self, request, **kwargs):
        try:
            issue_id = kwargs["issue_id"]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            issue = Issue.objects.get(issue_id)
        except Issue.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = IssueListSerializer(issue, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        try:
            issue_id = kwargs["issue_id"]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            issue = Issue.objects.get(id=issue_id)
        except Issue.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        issue.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NoteListView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request):
        notes = Note.objects.all()

        if "search" in request.GET and request.GET["search"] != "":
            notes = notes.filter(title__contains=request.GET["search"])

        serializer = NoteListSerializer(notes, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=NoteListSerializer)
    def post(self, request):
        serializer = NoteListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
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

    @swagger_auto_schema(request_body=NoteListSerializer)
    def patch(self, request, **kwargs):
        try:
            note_id = kwargs["note_id"]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            note = Note.objects.get(id=note_id)
        except Note.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = NoteListSerializer(note, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(method="delete")
    def delete(self, request, **kwargs):
        try:
            note_id = kwargs["note_id"]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            note = Note.objects.get(id=note_id)
        except Note.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TopicView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request):
        topics = Topic.objects.all()
        serilaizer = TopicSerializer(topics, many=True)
        return Response(serilaizer.data)

    @swagger_auto_schema(request_body=TopicSerializer)
    def post(self, request):
        serializer = TopicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class TopicDetailView(APIView):
    @swagger_auto_schema(request_body=TopicSerializer)
    def patch(self, request, **kwargs):
        try:
            topic_id = kwargs["topic_id"]
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            topic = Topic.objects.get(id=topic_id)
        except Topic.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = TopicSerializer(topic, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(method="delete")
    def delete(self, request, **kwargs):
        try:
            topic_id = kwargs["topic_id"]
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            topic = Topic.objects.get(id=topic_id)
        except Topic.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        topic.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PageView(APIView):
    @swagger_auto_schema(request_body=PageSerializer)
    def post(self, request):
        serializer = PageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
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

    @swagger_auto_schema(request_body=PageSerializer)
    def patch(self, request, **kwargs):
        try:
            page_id = kwargs["page_id"]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PageSerializer(page, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(method="delete")
    def delete(self, request, **kwargs):
        try:
            page_id = kwargs["page_id"]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
