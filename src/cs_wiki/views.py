from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView


class IssueListView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request):
        pass


class NoteListView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request, *args, **kwargs):
        pass


class PageDetailView(APIView):
    @swagger_auto_schema(method="get")
    def get(self, request, **kwargs):
        pass
