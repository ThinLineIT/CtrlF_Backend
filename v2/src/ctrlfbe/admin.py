from ctrlfbe.models import ContentRequest, Issue, Note, Page, PageComment, Topic
from django.contrib import admin

admin.site.register(Note)
admin.site.register(ContentRequest)
admin.site.register(Topic)
admin.site.register(Page)
admin.site.register(PageComment)
admin.site.register(Issue)
