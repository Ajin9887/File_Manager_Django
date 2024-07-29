from django.db import models
from django.utils import timezone
import uuid

from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    unique_id = models.CharField(max_length=255, default=uuid.uuid4, editable=False, unique=True)
    compressed_size = models.PositiveIntegerField(null=True, blank=True)
    original_size = models.PositiveIntegerField()
    file_type = models.CharField(max_length=50)

    def __str__(self):
        return self.file.name


    def is_expired(self):
        # Files expire after 10 days of upload
        expiration_date = self.uploaded_at + timezone.timedelta(days=10)
        return timezone.now() > expiration_date

    class Meta:
        db_table = 'file_uploads'
