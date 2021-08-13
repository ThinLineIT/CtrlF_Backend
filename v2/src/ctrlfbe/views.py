from typing import List

from rest_framework.views import APIView


class NoteAPIView(APIView):
    authentication_classes: List[str] = []
