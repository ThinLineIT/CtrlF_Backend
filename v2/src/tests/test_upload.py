from unittest.mock import Mock, patch

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status


class TestUpload(TestCase):
    S3_BASE_URL = settings.S3_BASE_URL
    S3_BUCKET_BASE_DIR = settings.S3_BUCKET_BASE_DIR

    def setUp(self) -> None:
        self.c = Client()

    def _call_api(self, request_body):
        return self.c.post(reverse("actions:upload_images"), request_body)

    @patch("common.s3.client.S3Client.upload_file_object", Mock())
    def test_should_return_url_containing_file_name(self):
        # Given: request body로 업로드 하려는 이미지의 정보가 주어진다.
        image_name = "dog.png"
        request_body = {"image": SimpleUploadedFile(name=image_name, content=b"image data", content_type="image/png")}

        # When: upload image api를 호출한다.
        response = self._call_api(request_body)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 응답으로 s3에 업로드된 이미지의 url을 리턴한다.
        expected_s3_image_url = f"{self.S3_BASE_URL}/{self.S3_BUCKET_BASE_DIR}/{image_name}"
        self.assertEqual(response.data["image_url"], expected_s3_image_url)
