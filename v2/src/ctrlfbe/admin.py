from ctrlfbe.models import Issue, Note, Page, PageHistory, Topic
from django.contrib import admin

admin.site.register(Note)
admin.site.register(Topic)
admin.site.register(Page)
admin.site.register(Issue)
admin.site.register(PageHistory)
