import environ

from .base import *  # noqa: F403, F401

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "mydatabase",
    }
}

env = environ.Env()
S3_BUCKET_NAME = env.str("S3_BUCKET_NAME", default="")
S3_BUCKET_BASE_DIR = env.str("S3_BUCKET_BASE_DIR", default="")
S3_BASE_URL = env.str("S3_BASE_URL", default="")

S3_AWS_ACCESS_KEY_ID = env.str("S3_AWS_ACCESS_KEY_ID", default="")
S3_AWS_SECRET_ACCESS_KEY = env.str("S3_AWS_SECRET_ACCESS_KEY", default="")
S3_AWS_REGION = env.str("S3_AWS_REGION", default="")
