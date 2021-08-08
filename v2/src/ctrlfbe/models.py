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


class ContentHistory(CommonTimestamp):
    user = models.ForeignKey(CtrlfUser, on_delete=models.CASCADE, help_text="수정 혹은 삭제의 주체자")
    sub_id = models.IntegerField(help_text="type에 대한 id")
    type = models.CharField(max_length=30, choices=CtrlfContentType.choices, help_text="NOTE, TOPIC, PAGE")
    action = models.CharField(max_length=30, choices=CtrlfActionType.choices, help_text="CRUD")
    reason = models.TextField(default="", help_text="수정 혹은 삭제 이유")

    def __str__(self):
        return f"{self.user}-{self.type}-{self.action}"


class Note(CommonTimestamp):
    owners = models.ManyToManyField(CtrlfUser)
    title = models.CharField(max_length=100)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Topic(CommonTimestamp):
    owners = models.ManyToManyField(CtrlfUser)
    note = models.ForeignKey("Note", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Page(CommonTimestamp):
    owners = models.ManyToManyField(CtrlfUser)
    topic = models.ForeignKey("Topic", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField(default="")

    def __str__(self):
        return self.title


class Issue(CommonTimestamp):
    owner = models.ForeignKey(CtrlfUser, on_delete=models.CASCADE, help_text="이슈를 생성한 사람")
    content_history = models.ForeignKey(
        "ContentHistory", on_delete=models.CASCADE, help_text="Issue와 관련된 content " "history"
    )
    title = models.CharField(max_length=100)
    content = models.TextField(default="")
    status = models.CharField(max_length=30, choices=CtrlfIssueStatus.choices, help_text="Issue 상태들")

    def __str__(self):
        return self.title
