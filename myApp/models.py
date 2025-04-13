from django.db import models

# Create your models here.
from django.db import models

class MediaFile(models.Model):
    MEDIA_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('file', 'File'),
    )

    url = models.URLField(max_length=500)
    file_name = models.CharField(max_length=255)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.media_type} - {self.file_name}"

from django.db import models
from django.utils.timezone import now

class VideoDownload(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    file_path = models.FileField(upload_to='videos/')
    downloaded_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.title} - {self.downloaded_at}"

from django.db import models

# To store the number of visits and downloads
class Statistics(models.Model):
    visits = models.IntegerField(default=0)
    image_downloads = models.IntegerField(default=0)
    video_downloads = models.IntegerField(default=0)
    movie_downloads = models.IntegerField(default=0)

    def increment_visits(self):
        self.visits += 1
        self.save()

    def increment_image_downloads(self):
        self.image_downloads += 1
        self.save()

    def increment_video_downloads(self):
        self.video_downloads += 1
        self.save()

    def increment_movie_downloads(self):
        self.movie_downloads += 1  # Corrected this line
        self.save()

    def __str__(self):
        return f"Visits: {self.visits}, Images: {self.image_downloads}, Videos: {self.video_downloads}, Movies: {self.movie_downloads}"




from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
