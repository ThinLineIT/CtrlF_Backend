from typing import List

# from ctrlf_auth.authentication import CtrlfAuthentication
# from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Note, Topic
from .serializers import NoteSerializer, TopicSerializer


class NoteDetailUpdateDeleteView(APIView):
    authentication_classes: List[str] = []

    def get(self, request, note_id):
        ERR_MSG = "노트를 찾을 수 없습니다."
        try:
            note = Note.objects.get(pk=note_id)
        except Note.DoesNotExist:
            return Response({"message": ERR_MSG}, status.HTTP_400_BAD_REQUEST)

        serializer = NoteSerializer(note)
        return Response(serializer.data, status.HTTP_200_OK)


class TopicListView(APIView):
    authentication_classes: List[str] = []

    def get(self, request, note_id):
        ERR_MSG = "노트를 찾을 수 없습니다."

        topics = Topic.objects.filter(note=note_id)

        if not len(topics):
            return Response({"message": ERR_MSG}, status.HTTP_400_BAD_REQUEST)

        serializer = TopicSerializer(topics, many=True)
        return Response(serializer.data, status.HTTP_200_OK)
