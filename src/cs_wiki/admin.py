from django.contrib import admin

from cs_wiki.models import Note, Issue, Page, Topic

admin.site.register(Note)
admin.site.register(Issue)
admin.site.register(Page)
admin.site.register(Topic)
