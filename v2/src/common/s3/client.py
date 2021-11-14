import boto3
from django.conf import settings


class S3Client:
    BUCKET_NAME = settings.S3_BUCKET_NAME

    def __init__(self):
        self.s3_client = boto3.client("s3")

    def upload_file(self, img_data, bucket_path):
        self.s3_client.upload_file(img_data, self.BUCKET_NAME, bucket_path)
