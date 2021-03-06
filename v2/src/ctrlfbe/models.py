from common.models import CommonTimestamp
from ctrlf_auth.models import CtrlfUser
from django.db import models, transaction


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

    @classmethod
    def can_be_closed(cls):
        return {cls.REJECTED, cls.REQUESTED}


class PageVersionType(models.TextChoices):
    CURRENT = "CURRENT", "최신"
    UPDATE = "UPDATE", "수정요청"
    PREVIOUS = "PREVIOUS", "과거"


class Note(CommonTimestamp):
    owners = models.ManyToManyField(CtrlfUser)
    title = models.CharField(max_length=100)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title}"

    def exists_owner(self, owner_id):
        return self.owners.filter(id=owner_id).exists()

    def process_update(self, title):
        self.title = title
        self.is_approved = True
        self.save()

    def process_create(self):
        with transaction.atomic():
            self.is_approved = True
            self.save()

    def process_delete(self):
        Issue.objects.filter(
            action=CtrlfActionType.DELETE, related_model_id=self.id, related_model_type=CtrlfContentType.NOTE
        ).delete()
        self.delete()


class Topic(CommonTimestamp):
    owners = models.ManyToManyField(CtrlfUser)
    note = models.ForeignKey("Note", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.note.title}-{self.title}"

    def exists_note_owner(self, owner_id):
        return self.note.owners.filter(id=owner_id).exists()

    def process_update(self, title):
        self.title = title
        self.is_approved = True
        self.save()

    def process_create(self):
        with transaction.atomic():
            self.is_approved = True
            self.save()

    def process_delete(self):
        Issue.objects.filter(
            action=CtrlfActionType.DELETE, related_model_id=self.id, related_model_type=CtrlfContentType.TOPIC
        ).delete()
        self.delete()


class Page(CommonTimestamp):
    owners = models.ManyToManyField(CtrlfUser)
    topic = models.ForeignKey("Topic", on_delete=models.CASCADE)

    def __str__(self):
        page_history = self.page_history.filter(version_type=PageVersionType.CURRENT).first()
        if page_history is None:
            return "page_history is None"
        return f"{self.topic.note.title}-{self.topic.title}-{page_history.title}"

    def exists_topic_owner(self, owner_id):
        return self.topic.owners.filter(id=owner_id).exists()

    def process_update(self):
        with transaction.atomic():
            prev_page_history = PageHistory.page_version.current(self).first()
            prev_page_history.version_type = PageVersionType.PREVIOUS
            prev_page_history.save()

            new_page_history = PageHistory.page_version.to_update(self).first()
            new_page_history.is_approved = True
            new_page_history.version_type = PageVersionType.CURRENT
            new_page_history.save()

            self.title = new_page_history.title
            self.content = new_page_history.content
            self.is_approved = True
            self.save()

    def process_create(self):
        with transaction.atomic():
            self.is_approved = True
            self.save()

            page_history = self.page_history.first()
            if page_history:
                page_history.is_approved = True
                page_history.save()

    def process_delete(self):
        Issue.objects.filter(
            action=CtrlfActionType.DELETE, related_model_id=self.id, related_model_type=CtrlfContentType.PAGE
        ).delete()
        self.delete()


class PageHistoryQuerySet(models.QuerySet):
    def current(self, page):
        return self.filter(page=page, version_type=PageVersionType.CURRENT)

    def to_update(self, page):
        return self.filter(page=page, version_type=PageVersionType.UPDATE)


class PageHistory(CommonTimestamp):
    owner = models.ForeignKey(CtrlfUser, on_delete=models.CASCADE)
    page = models.ForeignKey(Page, related_name="page_history", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    version_no = models.IntegerField(default=1)
    version_type = models.CharField(max_length=30, choices=PageVersionType.choices)
    objects = models.Manager()

    page_version = PageHistoryQuerySet.as_manager()

    def __str__(self):
        return f"page_id:{self.page_id}-title:{self.title}-version:{self.version_no}"


class Issue(CommonTimestamp):
    owner = models.ForeignKey(CtrlfUser, on_delete=models.CASCADE, help_text="이슈를 생성한 사람")
    title = models.CharField(max_length=100)
    reason = models.TextField(default="", help_text="NOTE, TOPIC, PAGE CRUD에 대한 설명")
    status = models.CharField(max_length=30, choices=CtrlfIssueStatus.choices, help_text="Issue 상태들")
    related_model_type = models.CharField(
        max_length=30, choices=CtrlfContentType.choices, help_text="NOTE, TOPIC, PAGE"
    )
    related_model_id = models.IntegerField(default=0, help_text="note_id, topic_id, page_history_id")
    action = models.CharField(max_length=30, default="", choices=CtrlfActionType.choices, help_text="CRUD")
    etc = models.CharField(max_length=300, null=True, help_text="legacy title을 저장하는 용도 및 다양하게 사용")

    def __str__(self):
        return f"{self.title}-{self.related_model_type}-{self.related_model_id}"

    def get_ctrlf_content(self):
        page_history = PageHistory.objects.filter(id=self.related_model_id).first()
        page = page_history and page_history.page
        return {
            CtrlfContentType.PAGE: page,
            CtrlfContentType.NOTE: Note.objects.filter(id=self.related_model_id).first(),
            CtrlfContentType.TOPIC: Topic.objects.filter(id=self.related_model_id).first(),
        }.get(self.related_model_type)
