from .base import *  # noqa: F403, F401

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("RDS_DB_NAME", ""),  # noqa: F405
        "USER": os.environ.get("RDS_USERNAME", ""),  # noqa: F405
        "PASSWORD": os.environ.get("RDS_PASSWORD", ""),  # noqa: F405
        "HOST": os.environ.get("RDS_HOSTNAME", ""),  # noqa: F405
        "PORT": os.environ.get("RDS_PORT", ""),  # noqa: F405
    }
}
