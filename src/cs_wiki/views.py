from django.http import JsonResponse, HttpResponse, response
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from cs_wiki.models import Note, Page, Issue, Topic
from cs_wiki.serializers import NoteListSerializer, AllPageCountViewSerializer, IssueListViewSerializer, DetailPageViewSerializer, TopicListSerializer, PageListSerializer, NoteDetailViewSerializer

from drf_yasg import openapi
from rest_framework import status


class CategoryListView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request):
        return Response({"Hello": "Category"})


class NoteListView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request):
        notes = Note.objects.all()
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


class AllPageCountView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request):
        count = Page.objects.all().count()
        serializer = AllPageCountViewSerializer(count)
        return Response(serializer.data)


class NoteDetailView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request, note_id):
        try:
            note = (Note.objects.prefetch_related(
                "topic_set", "topic_set__page_set").get(id=note_id))
        except Note.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = NoteDetailViewSerializer(note)
        return Response(serializer.data)


class IssueListView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request):
        issues = Issue.objects.all()
        serializer = IssueListViewSerializer(issues, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=IssueListViewSerializer)
    def post(self, request):
        serializer = IssueListViewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class PageDetailView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request, page_id):
        page = Page.objects.get(id=page_id)
        serializer = DetailPageViewSerializer(page)
        return Response(serializer.data)


class TopicListView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request):
        topics = Topic.objects.all()
        serializer = TopicListSerializer(topics, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=TopicListSerializer)
    def post(self, request):
        serializer = TopicListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class PageListView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request):
        pages = Page.objects.all()
        serializer = PageListSerializer(pages, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=PageListSerializer)
    def post(self, request):
        serializer = PageListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
