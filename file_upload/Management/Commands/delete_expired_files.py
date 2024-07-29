
# file_upload/management/commands/delete_expired_files.py

from django.core.management.base import BaseCommand
from file_upload.models import UploadedFile
from django.utils import timezone

class Command(BaseCommand):
    help = 'Delete expired files'

    def handle(self, *args, **kwargs):
        expired_files = UploadedFile.objects.filter(uploaded_at__lte=timezone.now() - timezone.timedelta(days=10))  # Point c
        for file in expired_files:
            file.file.delete()
            file.delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted expired files'))
