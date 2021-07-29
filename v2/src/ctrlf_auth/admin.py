from ctrlf_auth.models import CtrlfUser, EmailAuthCode
from django.contrib import admin

admin.site.register(CtrlfUser)
admin.site.register(EmailAuthCode)
