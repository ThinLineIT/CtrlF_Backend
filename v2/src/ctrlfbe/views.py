from typing import List

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import ERR_MSG
from .models import Note
from .serializers import NoteSerializer


class NoteDetailUpdateDeleteView(APIView):
    authentication_classes: List[str] = []

    @swagger_auto_schema(responses={200: NoteSerializer()})
    def get(self, request, note_id):
        try:
            note = Note.objects.get(pk=note_id)
        except Note.DoesNotExist:
            return Response({"message": ERR_MSG}, status.HTTP_404_NOT_FOUND)

        serializer = NoteSerializer(note)
        return Response(serializer.data, status.HTTP_200_OK)
