from django.contrib import admin
from batchsql.models import QueuedJob, CompletedJob

admin.site.register(QueuedJob)
admin.site.register(CompletedJob)
