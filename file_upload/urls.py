from django.urls import path
from django.conf.urls.static import static
from file_upload_project import settings
from . import views

urlpatterns = [
    path('upload/', views.upload_form, name='upload_form'),
    path('file/<uuid:unique_id>/', views.file_detail, name='file_detail'),
    path('download_compressed/<uuid:unique_id>/', views.download_compressed_file, name='download_compressed_file'),
    path('file/<uuid:unique_id>/download/<int:duration>/', views.download_video_segment, name='download_video_segment'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

