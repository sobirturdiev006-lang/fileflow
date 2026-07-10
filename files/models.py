import uuid

from django.db import models


def upload_to_input(instance, filename):
    return f"inputs/{instance.id}/{filename}"


def upload_to_output(instance, filename):
    return f"outputs/{instance.id}/{filename}"


class ProcessingJob(models.Model):
    """
    Foydalanuvchi yuklagan faylni qayta ishlash uchun bitta "job".
    Auth keyin qo'shilganda `user` FK ishlatiladi, hozircha nullable.
    """

    class JobType(models.TextChoices):
        EXCEL_CLEAN = "excel_clean", "Excel tozalash/deduplikatsiya"
        EXCEL_TO_PDF = "excel_to_pdf", "Excel -> PDF hisobot"
        PDF_TABLE_EXTRACT = "pdf_table_extract", "PDF jadval -> Excel"
        DOCX_TO_PDF = "docx_to_pdf", "Word -> PDF"
        PDF_TEXT_EXTRACT = "pdf_text_extract", "PDF matn -> Word"

    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        PROCESSING = "processing", "Qayta ishlanmoqda"
        DONE = "done", "Tayyor"
        FAILED = "failed", "Xatolik"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    job_type = models.CharField(max_length=32, choices=JobType.choices)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)

    input_file = models.FileField(upload_to=upload_to_input)
    result_file = models.FileField(upload_to=upload_to_output, blank=True, null=True)

    error_message = models.TextField(blank=True, default="")

    # job_type ga qarab qo'shimcha parametrlar (masalan dedup uchun ustun nomi)
    options = models.JSONField(blank=True, default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.job_type} [{self.status}] {self.id}"