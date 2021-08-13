from typing import List

from ctrlfbe.models import Note
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class NoteAPIView(APIView):
    authentication_classes: List[str] = []

    def get(self, request):
        current_cursor = int(request.query_params["cursor"])
        notes = Note.objects.all()[current_cursor : current_cursor + 30]
        response_notes = []

        for index, note in enumerate(notes):
            response_notes.append(
                {
                    "id": index + 1,
                    "title": note.title,
                    "is_approved": note.is_approved,
                }
            )
        next_cursor = current_cursor + len(response_notes)

        return Response(data={"next_cursor": next_cursor, "notes": response_notes}, status=status.HTTP_200_OK)
