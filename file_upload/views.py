from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, FileResponse, Http404
from .models import UploadedFile
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import uuid
from PIL import Image
import io
import os
import ffmpeg
from django.utils import timezone
import datetime
from urllib.parse import urljoin

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def upload_form(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return HttpResponse('No file selected.')

        # Fetch the client's IP address
        client_ip = get_client_ip(request)

        # Calculate the start of the current day
        start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Count the number of uploads from this IP address today
        uploads_today = UploadedFile.objects.filter(ip_address=client_ip, uploaded_at__gte=start_of_day).count()

        if uploads_today >= 10:
            return HttpResponseForbidden("You have reached the upload limit for today.")

        # Determine file type
        if uploaded_file.content_type.startswith('image'):
            file_type = 'image'
        elif uploaded_file.content_type == 'application/pdf':
            file_type = 'pdf'
        elif uploaded_file.content_type.startswith('video'):
            file_type = 'video'
        else:
            file_type = 'other'

        if file_type == 'image':
            # Compress the image
            image = Image.open(uploaded_file)
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=70)  # Adjust quality as needed
            compressed_image = output.getvalue()
            compressed_size = len(compressed_image)

            # Create new UploadedFile instance
            uploaded_file_obj = UploadedFile.objects.create(
                file=uploaded_file,
                ip_address=client_ip,
                unique_id=str(uuid.uuid4()),
                compressed_size=compressed_size,
                original_size=uploaded_file.size,
                file_type=file_type
            )

            # Ensure the directory exists
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            ensure_directory_exists(upload_dir)

            # Save the compressed image
            fs = FileSystemStorage(location=upload_dir)
            compressed_filename = f'{uploaded_file_obj.unique_id}.jpg'
            fs.save(compressed_filename, io.BytesIO(compressed_image))

            return HttpResponse(f'Short link: /file/{uploaded_file_obj.unique_id}/')

        elif file_type == 'video':
            if uploaded_file.size > 50 * 1024 * 1024:  # 50 MB limit
                return HttpResponse('File size exceeds the limit (50 MB).')

            # Create new UploadedFile instance
            uploaded_file_obj = UploadedFile.objects.create(
                file=uploaded_file,
                ip_address=client_ip,
                unique_id=str(uuid.uuid4()),
                original_size=uploaded_file.size,
                file_type=file_type
            )

            # Ensure the directory exists
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            ensure_directory_exists(upload_dir)

            # Save the original video file
            fs = FileSystemStorage(location=upload_dir)
            video_filename = fs.save(uploaded_file.name, uploaded_file)

            # Compress the video
            input_path = os.path.join(upload_dir, video_filename)
            compressed_filename = f'{uploaded_file_obj.unique_id}_compressed.mp4'
            compressed_path = os.path.join(upload_dir, compressed_filename)

            # Perform video compression using ffmpeg
            ffmpeg.input(input_path).output(compressed_path, video_bitrate='500k').run()

            # Get the compressed file size
            compressed_size = os.path.getsize(compressed_path)

            # Update the UploadedFile instance with compressed file size
            uploaded_file_obj.compressed_size = compressed_size
            uploaded_file_obj.save()

            return HttpResponse(f'Short link: /file/{uploaded_file_obj.unique_id}/')

        else:
            uploaded_file_obj = UploadedFile.objects.create(
                file=uploaded_file,
                ip_address=client_ip,
                unique_id=str(uuid.uuid4()),
                original_size=uploaded_file.size,
                file_type=file_type
            )
            return HttpResponse(f'Short link: /file/{uploaded_file_obj.unique_id}/')
    return render(request, 'file_upload/upload_form.html')

def file_detail(request, unique_id):
    file_obj = get_object_or_404(UploadedFile, unique_id=unique_id)

    # Calculate file size in MB
    file_size_mb = round(file_obj.file.size / (1024 * 1024), 2)

    # Calculate compressed file size in MB if available
    compressed_file_size_mb = round(file_obj.compressed_size / (1024 * 1024), 2) if file_obj.compressed_size else None

    # Construct compressed file URL
    compressed_file_url = None
    if compressed_file_size_mb:
        compressed_filename = f'{unique_id}_compressed.mp4'
        compressed_file_url = urljoin(settings.MEDIA_URL, f'uploads/{compressed_filename}')

    # Convert the uploaded_at timestamp to IST
    utc_time = file_obj.uploaded_at
    ist_time = utc_time + datetime.timedelta(hours=5, minutes=30)

    return render(request, 'file_upload/file_detail.html', {
        'file': file_obj,
        'file_size_mb': file_size_mb,
        'compressed_file_size_mb': compressed_file_size_mb,
        'compressed_file_url': compressed_file_url,
        'ist_time': ist_time,
    })

def redirect_to_upload_form(request):
    return redirect('upload_form')

def delete_expired_files():
    expired_files = UploadedFile.objects.filter(uploaded_at__lte=timezone.now() - timezone.timedelta(days=10))
    for file in expired_files:
        file.file.delete()
        file.delete()

def download_video_segment(request, unique_id, duration):
    file_obj = get_object_or_404(UploadedFile, unique_id=unique_id)
    if file_obj.file_type != 'video':
        return HttpResponse('Requested file is not a video.')

    start_time = 0
    duration = int(duration)

    input_path = file_obj.file.path
    output_path = os.path.join(settings.MEDIA_ROOT, f'{unique_id}_{duration}s.mp4')

    ffmpeg.input(input_path, ss=start_time, t=duration).output(output_path).run()

    with open(output_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='video/mp4')
        response['Content-Disposition'] = f'attachment; filename="{unique_id}_{duration}s.mp4"'
        return response

def download_compressed_file(request, unique_id):
    file_obj = get_object_or_404(UploadedFile, unique_id=unique_id)

    compressed_filename = f'{unique_id}_compressed.mp4'
    compressed_path = os.path.join(settings.MEDIA_ROOT, 'uploads', compressed_filename)

    if not os.path.exists(compressed_path):
        raise Http404("Compressed file does not exist")

    return FileResponse(open(compressed_path, 'rb'), as_attachment=True, filename=compressed_filename)
