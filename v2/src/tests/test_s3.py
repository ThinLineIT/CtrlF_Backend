import os

import boto3
from django.test import Client, TestCase


class TestImageUpload(TestCase):
    BUCKET_NAME = "testing-for-jinho"
    BUCKET_BASE_DIR = "temp"

    def setUp(self) -> None:
        self.s3 = boto3.client("s3")
        self.c = Client()

    def test_upload_file(self):
        to_upload_file_name = "dog.png"
        to_upload_file_location = os.path.join(os.getcwd(), to_upload_file_name)
        upload_bucket_location = "/".join([self.BUCKET_BASE_DIR, to_upload_file_name])

        self.s3.upload_file(to_upload_file_location, self.BUCKET_NAME, upload_bucket_location,
                            ExtraArgs={"ContentType": "image/png", })
        object_url = "https://d2af9nad0zcf09.cloudfront.net/{0}".format(upload_bucket_location)
        print(object_url)

    def tearDown(self) -> None:
        pass
        # data = self.s3.delete_object(Bucket=self.BUCKET_NAME, Key="temp/dog.png")
