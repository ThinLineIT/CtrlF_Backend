from django.http import JsonResponse, HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from cs_wiki.models import Note, Page
from cs_wiki.serializers import NoteSerializer, AllPageCountViewSerializer


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
        return JsonResponse({"count": count})
