import boto3
from django.conf import settings


class S3Client:
    BUCKET_NAME = settings.S3_BUCKET_NAME
    S3_AWS_ACCESS_KEY_ID = settings.S3_AWS_ACCESS_KEY_ID
    S3_AWS_SECRET_ACCESS_KEY = settings.S3_AWS_SECRET_ACCESS_KEY
    S3_AWS_REGION = settings.S3_AWS_REGION

    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.S3_AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.S3_AWS_SECRET_ACCESS_KEY,
            region_name=self.S3_AWS_REGION,
        )

    def upload_file_object(self, image_data, bucket_path, content_type):
        self.s3_client.upload_fileobj(
            image_data, self.BUCKET_NAME, bucket_path, ExtraArgs={"ContentType": content_type}
        )
