import tempfile

import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from .models import ProcessingJob
from .services import process_excel_clean


def _make_excel_upload(rows, columns):
    """Berilgan qatorlardan vaqtinchalik .xlsx fayl yaratib, Django upload
    fayl obyektiga aylantiradi."""
    df = pd.DataFrame(rows, columns=columns)
    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    df.to_excel(tmp.name, index=False)
    tmp.seek(0)
    with open(tmp.name, "rb") as f:
        content = f.read()
    return SimpleUploadedFile("input.xlsx", content)


class ProcessExcelCleanTests(TestCase):
    def setUp(self):
        self.tmp_media = tempfile.mkdtemp()
        self._override = override_settings(MEDIA_ROOT=self.tmp_media)
        self._override.enable()

    def tearDown(self):
        self._override.disable()

    def test_removes_fully_empty_rows(self):
        upload = _make_excel_upload(
            rows=[["A", 1], [None, None], ["B", 2]],
            columns=["name", "value"],
        )
        job = ProcessingJob.objects.create(
            job_type=ProcessingJob.JobType.EXCEL_CLEAN,
            input_file=upload,
        )

        result_relpath = process_excel_clean(job)
        result_df = pd.read_excel(f"{self.tmp_media}/{result_relpath}")

        self.assertEqual(len(result_df), 2)
        self.assertListEqual(list(result_df["name"]), ["A", "B"])

    def test_removes_duplicate_rows_across_all_columns(self):
        upload = _make_excel_upload(
            rows=[["A", 1], ["A", 1], ["B", 2]],
            columns=["name", "value"],
        )
        job = ProcessingJob.objects.create(
            job_type=ProcessingJob.JobType.EXCEL_CLEAN,
            input_file=upload,
        )

        result_relpath = process_excel_clean(job)
        result_df = pd.read_excel(f"{self.tmp_media}/{result_relpath}")

        self.assertEqual(len(result_df), 2)

    def test_dedup_by_specific_column_only(self):
        upload = _make_excel_upload(
            rows=[["A", 1], ["A", 2], ["B", 3]],
            columns=["name", "value"],
        )
        job = ProcessingJob.objects.create(
            job_type=ProcessingJob.JobType.EXCEL_CLEAN,
            input_file=upload,
            options={"dedup_columns": ["name"]},
        )

        result_relpath = process_excel_clean(job)
        result_df = pd.read_excel(f"{self.tmp_media}/{result_relpath}")

        # "name" ustuni bo'yicha dedup qilingani uchun "A" faqat 1 marta qoladi
        self.assertEqual(len(result_df), 2)
        self.assertListEqual(sorted(result_df["name"]), ["A", "B"])


class ProcessingJobModelTests(TestCase):
    def test_str_representation_includes_type_and_status(self):
        job = ProcessingJob.objects.create(
            job_type=ProcessingJob.JobType.EXCEL_TO_PDF,
        )
        self.assertIn("excel_to_pdf", str(job))
        self.assertIn("pending", str(job))