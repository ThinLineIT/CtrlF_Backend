import os
import unittest
from unittest.mock import patch, Mock

import boto3
import ipdb
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status


class TestUpload(TestCase):
    BUCKET_NAME = "testing-for-jinho"
    BUCKET_BASE_DIR = "temp"

    def setUp(self) -> None:
        self.s3 = boto3.client("s3")
        self.c = Client()

    def _call_api(self, request_body):
        return self.c.post(reverse("actions:upload_images"), request_body)

    @patch("common.s3.client.S3Client.upload_file", Mock())
    def test_should_upload_text_file_to_s3_bucket(self):
        # Given: request body로 업로드 하려는 이미지의 경로가 주어진다.
        request_body = {"img_data": "/dog.png"}

        # When: upload image api를 호출한다.
        response = self._call_api(request_body)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: 응답 url은 expexted 이어야 한다
        expected = "https://d2af9nad0zcf09.cloudfront.net/temp/dog.png"
        self.assertEqual(response.data["image_url"], expected)
