from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
"""
config/urls.py — namuna.
Mavjud loyihangizdagi DRF router qismini saqlab qolib, shunchaki
`files.urls` (template) ni qo'shing va MEDIA_URL'ni DEBUG holatda serve qiling.
"""

from rest_framework.routers import DefaultRouter

from files.views import ProcessingJobViewSet

router = DefaultRouter()
# basename="job" -> "job-list" / "job-detail" nomlari hosil bo'ladi,
# bular app.js ichidagi {% url 'job-list' %} bilan mos kelishi kerak edi,
# shu sababli basename'ni aniq "job" qilib belgilaymiz:
router.register(r"jobs", ProcessingJobViewSet, basename="job")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("", include("files.urls", namespace="files")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
