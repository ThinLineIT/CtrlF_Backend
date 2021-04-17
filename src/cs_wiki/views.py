from django.http import JsonResponse, HttpResponse, response
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from cs_wiki.models import Note, Page, Issue, Topic
from cs_wiki.serializers import NoteSerializer, AllPageCountViewSerializer, IssueListViewSerializer, DetailPageViewSerializer


@swagger_auto_schema(method="get")
class CategoryListView(APIView):
    def get(self, request):
        return Response({"Hello": "Category"})


@swagger_auto_schema(method="get")
class NoteListView(APIView):
    def get(self, request):
        notes = Note.objects.all()
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)


@swagger_auto_schema(method="get")
class AllPageCountView(APIView):
    def get(self, request):
        count = Page.objects.all().count()
        serializer = AllPageCountViewSerializer(count)
        return Response(serializer.data)


@swagger_auto_schema(method="get")
class IssueListView(APIView):
    def get(self, request):
        issues = Issue.objects.all()
        serializer = IssueListViewSerializer(issues, many=True)
        return Response(serializer.data)


@swagger_auto_schema(method="get")
class PageDetailView(APIView):
    def get(self, request, page_id):
        page = Page.objects.get(id=page_id)
        serializer = DetailPageViewSerializer(page)
        return Response(serializer.data)
