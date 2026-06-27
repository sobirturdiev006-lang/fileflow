from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import ProcessingJob
from .serializers import ProcessingJobCreateSerializer, ProcessingJobDetailSerializer
from .tasks import process_job


class ProcessingJobViewSet(viewsets.ModelViewSet):
    """
    POST   /api/jobs/        -> fayl yuklash, job yaratish, Celery taskni ishga tushirish
    GET    /api/jobs/        -> barcha joblar ro'yxati
    GET    /api/jobs/{id}/   -> bitta job holati va natijasi
    """
    queryset = ProcessingJob.objects.all()
    http_method_names = ["get", "post", "head"]

    def get_serializer_class(self):
        if self.action == "create":
            return ProcessingJobCreateSerializer
        return ProcessingJobDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job = serializer.save()

        process_job.delay(str(job.id))

        detail = ProcessingJobDetailSerializer(job, context={"request": request})
        return Response(detail.data, status=status.HTTP_201_CREATED)
