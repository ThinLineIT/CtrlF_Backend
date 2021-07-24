from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    # S3 전용 Media 파일들 처리 저장소
    location = "media"
    file_overwrite = False
