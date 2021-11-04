from common.models import CommonTimestamp
from ctrlf_auth.models import CtrlfUser
from django.db import models


class CtrlfContentType(models.TextChoices):
    NOTE = "NOTE", "노트"
    TOPIC = "TOPIC", "토픽"
    PAGE = "PAGE", "페이지"


class CtrlfActionType(models.TextChoices):
    CREATE = "CREATE", "생성"
    UPDATE = "UPDATE", "수정"
    DELETE = "DELETE", "삭제"


class CtrlfIssueStatus(models.TextChoices):
    REQUESTED = "REQUESTED", "요청"
    REJECTED = "REJECTED", "거절"
    APPROVED = "APPROVED", "승인"
    CLOSED = "CLOSED", "닫힘"


class CtrlfBaseContent(models.Model):
    owners = models.ManyToManyField(CtrlfUser)
    title = models.CharField(max_length=100, default="")
    is_approved = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Note(CommonTimestamp, CtrlfBaseContent):
    def __str__(self):
        return self.title


class Topic(CommonTimestamp, CtrlfBaseContent):
    note = models.ForeignKey("Note", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.note.title}-{self.title}"


class Page(CommonTimestamp, CtrlfBaseContent):
    topic = models.ForeignKey("Topic", on_delete=models.CASCADE)
    content = models.TextField(default="")

    def __str__(self):
        return f"{self.topic.note.title}-{self.topic.title}-{self.title}"


class Issue(CommonTimestamp):
    owner = models.ForeignKey(CtrlfUser, on_delete=models.CASCADE, help_text="이슈를 생성한 사람")
    title = models.CharField(max_length=100)
    reason = models.TextField(default="")
    status = models.CharField(max_length=30, choices=CtrlfIssueStatus.choices, help_text="Issue 상태들")
    content_type = models.CharField(
        max_length=30, default="", choices=CtrlfContentType.choices, help_text="NOTE, TOPIC, PAGE"
    )
    content_id = models.IntegerField(default=0, help_text="note_id, topic_id, page_id")
    action = models.CharField(max_length=30, default="", choices=CtrlfActionType.choices, help_text="CRUD")

    def __str__(self):
        return self.title
