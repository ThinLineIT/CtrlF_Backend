import os
import unittest

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

    def test_should_upload_text_file_to_s3_bucket(self):
        # Given: request body로 업로드 하려는 이미지의 경로가 주어진다.
        filename = "test.txt"
        request_body = {"img_data": os.path.join(os.getcwd(), filename)}
        bucket_dir = "/".join([self.BUCKET_BASE_DIR, filename])

        # When: upload image api를 호출한다.
        response = self._call_api(request_body)

        # Then: status code는 200을 리턴한다.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And: s3 bucket에 이미지가 업로드 되어있다.
        self.assertIsNotNone(self.s3.get_object(Bucket=self.BUCKET_NAME, Key=bucket_dir))

    def tearDown(self) -> None:
        pass
        # self.s3.delete_object(Bucket=self.BUCKET_NAME, Key=self.BUCKET_DIR)
