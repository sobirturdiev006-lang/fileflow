from django.contrib import admin

from .models import ProcessingJob


@admin.register(ProcessingJob)
class ProcessingJobAdmin(admin.ModelAdmin):
    list_display = ["id", "job_type", "status", "created_at", "updated_at"]
    list_filter = ["job_type", "status"]
    readonly_fields = ["id", "created_at", "updated_at"]
