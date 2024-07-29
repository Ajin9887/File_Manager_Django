# Generated by Django 5.0.6 on 2024-05-29 02:17

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='uploads/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('unique_id', models.CharField(default=uuid.uuid4, editable=False, max_length=255, unique=True)),
                ('compressed_size', models.PositiveIntegerField(blank=True, null=True)),
                ('original_size', models.PositiveIntegerField()),
                ('file_type', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'file_uploads',
            },
        ),
    ]