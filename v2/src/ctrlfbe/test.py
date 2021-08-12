from ctrlf_auth.models import CtrlfUser
from ctrlfbe.models import Note
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status


class TestNoteDetail(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = CtrlfUser.objects.create_user(email="test@test.com", password="12345")
        self.note = Note.objects.create(title="test note")
        self.note.owners.add(self.user)

    def test_note_detail_should_return_200(self):
        # Given: 정상적인 note id
        note_id = self.note.id
        # When : API 실행
        response = self.c.get(reverse("notes:note_detail_update_delete", kwargs={"note_id": note_id}))
        # Then : 상태코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And  : 미리 생성했던 정보와 일치해야 함.
        data = response.data
        self.assertEqual(data["id"], note_id)
        self.assertEqual(data["title"], self.note.title)
        self.assertEqual(data["is_approved"], self.note.is_approved)
        self.assertIn(self.user.id, data["owners"])
