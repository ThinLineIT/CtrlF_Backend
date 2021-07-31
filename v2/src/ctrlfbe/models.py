from ctrlf_auth.models import CtrlfUser
from django.db import models


class Note(models.Model):
    user = models.ForeignKey(CtrlfUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    is_approved = models.BooleanField(default=False)
    request_contents = models.CharField(max_length=300)

    def __str__(self):
        return self.title
