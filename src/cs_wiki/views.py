from django.http import JsonResponse, HttpResponse, response
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from cs_wiki.models import Note, Page, Issue, Topic
from cs_wiki.serializers import NoteListSerializer, AllPageCountViewSerializer, IssueListViewSerializer, DetailPageViewSerializer, TopicListSerializer, PageListSerializer  # AllPageListViewSerializer

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


class AllPageListView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request):
        print(request)
        serializer = AllPageListViewSerializer()
        return Response(serializer.data)


class IssueListView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request):
        issues = Issue.objects.all()
        serializer = IssueListViewSerializer(issues, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TopicListSerializer(data=request.data)
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
    def post(self, request):
        serializer = TopicListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class PageListView(APIView):
    def post(self, request):
        print(request)
        serializer = PageListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
