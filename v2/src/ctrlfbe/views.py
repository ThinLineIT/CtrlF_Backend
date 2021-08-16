from typing import List

from ctrlfbe.models import Note
from ctrlfbe.serializers import NoteSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class NoteAPIView(APIView):
    authentication_classes: List[str] = []

    @swagger_auto_schema(query_serializer=NoteSerializer)
    def get(self, request):
        current_cursor = int(request.query_params["cursor"])
        notes = Note.objects.all()[current_cursor : current_cursor + 30]
        serializer = NoteSerializer(notes, many=True)
        serialized_notes = serializer.data
        return Response(
            data={"next_cursor": current_cursor + len(serialized_notes), "notes": serialized_notes},
            status=status.HTTP_200_OK,
        )
