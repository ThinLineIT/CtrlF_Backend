from .base import *  # noqa: F403, F401

AWS_STORAGE_BUCKET_NAME = "ctrl-be"
AWS_PRELOAD_METADATA = True
AWS_QUERYSTRING_AUTH = False
AWS_S3_REGION_NAME = "ap-northeast-2"
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_S3_CUSTOM_DOMAIN = "%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_STATIC_LOCATION = "static"
AWS_MEDIA_LOCATION = "media"
