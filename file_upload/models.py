
# file_upload/models.py
""""
import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    ip_address = models.CharField(max_length=45)
    unique_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_image = models.BooleanField(default=False)
    is_pdf = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.uploaded_at + timedelta(days=10)


from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    ip_address = models.CharField(max_length=45)
    unique_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_image = models.BooleanField(default=False)
    is_pdf = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    original_size = models.PositiveIntegerField(null=True, blank=True)
    compressed_size = models.PositiveIntegerField(null=True, blank=True)

    def is_expired(self):
        return timezone.now() > self.uploaded_at + timedelta(days=10)

"""

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