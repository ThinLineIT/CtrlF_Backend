import os

from celery import Celery
from config.settings.base import PLATFORM_ENV

os.environ.setdefault("DJANGO_SETTINGS_MODULE", PLATFORM_ENV)

app = Celery("config")
app.conf.broker_url = "redis://localhost:6379/0"

# app.config_from_object('django.conf:config.settings.local', namespace='CELERY')

app.autodiscover_tasks()


@app.task
def add(x, y):
    return x + y
