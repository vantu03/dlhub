from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from ckeditor.fields import RichTextField

class Upload(models.Model):
    source_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    thumbnail = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Upload: {self.title}"

    def delete(self, *args, **kwargs):
        for f in self.files.all():
            f.delete()
        super().delete(*args, **kwargs)

class File(models.Model):
    upload = models.ForeignKey(Upload, related_name='files', on_delete=models.CASCADE)
    url = models.URLField()
    label = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.label} - {self.url}"

    def delete(self, *args, **kwargs):
        # Xóa file thật nếu còn tồn tại
        from django.conf import settings
        import os
        path = self.url
        if path.startswith("/media/"):
            full_path = os.path.join(settings.BASE_DIR, path.lstrip("/"))
            if os.path.isfile(full_path):
                try:
                    os.remove(full_path)
                    print(f"Deleted: {full_path}")
                except Exception as e:
                    print(f"Failed to delete {full_path}: {e}")
            else:
                print(f"Failed to delete {full_path}")
        super().delete(*args, **kwargs)


class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    summary = models.CharField(max_length=255, blank=True)
    content = RichTextField()
    cover_image = models.URLField(blank=True, null=True)
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='articles')
    tags = models.CharField(max_length=255, blank=True, help_text="Enter keywords, analyze using comma")

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_tags(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
