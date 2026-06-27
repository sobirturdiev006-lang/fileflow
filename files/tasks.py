import logging

from celery import shared_task

from .models import ProcessingJob
from .services import PROCESSORS

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=1)
def process_job(self, job_id):
    try:
        job = ProcessingJob.objects.get(id=job_id)
    except ProcessingJob.DoesNotExist:
        logger.error("Job topilmadi: %s", job_id)
        return

    job.status = ProcessingJob.Status.PROCESSING
    job.save(update_fields=["status", "updated_at"])

    processor = PROCESSORS.get(job.job_type)
    if processor is None:
        job.status = ProcessingJob.Status.FAILED
        job.error_message = f"Noma'lum job_type: {job.job_type}"
        job.save(update_fields=["status", "error_message", "updated_at"])
        return

    try:
        relative_result_path = processor(job)
        job.result_file.name = relative_result_path
        job.status = ProcessingJob.Status.DONE
        job.save(update_fields=["status", "result_file", "updated_at"])
    except Exception as exc:
        logger.exception("Job %s ishlov berishda xato", job_id)
        job.status = ProcessingJob.Status.FAILED
        job.error_message = str(exc)
        job.save(update_fields=["status", "error_message", "updated_at"])
