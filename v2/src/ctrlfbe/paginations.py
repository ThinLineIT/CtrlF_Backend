from ctrlfbe.constants import MAX_PRINTABLE_NOTE_COUNT
from ctrlfbe.models import Note
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response


class NoteListPagination(CursorPagination):
    max_page_size = MAX_PRINTABLE_NOTE_COUNT

    def paginate_queryset(self, queryset, request, view=None):
        self.current_cursor = int(request.query_params["cursor"])
        notes = Note.objects.all()[self.current_cursor : self.current_cursor + MAX_PRINTABLE_NOTE_COUNT]
        return notes

    def get_paginated_response(self, data):
        return Response(data={"next_cursor": self.current_cursor + len(data), "notes": data})


class IssueListPagination(CursorPagination):
    max_page_size = MAX_PRINTABLE_NOTE_COUNT

    def paginate_queryset(self, queryset, request, view=None):
        self.current_cursor = int(request.query_params["cursor"])
        issues = queryset[self.current_cursor : self.current_cursor + MAX_PRINTABLE_NOTE_COUNT]
        return issues

    def get_paginated_response(self, data):
        return Response(data={"next_cursor": self.current_cursor + len(data), "issues": data})
