from django.db import models
from django.utils import timezone

class DownloadRecord(models.Model):
    url = models.URLField()
    urls = models.JSONField()
    thumbnail = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    title = models.TextField(max_length=255)

    def __str__(self):
        return f"[{self.platform.upper()}] {self.url} ({len(self.urls)} files)"
