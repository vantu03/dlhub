from django.db import models
from django.utils import timezone
from django.urls import reverse
from bs4 import BeautifulSoup
from django.templatetags.static import static
import os
from tinymce.models import HTMLField
from mimetypes import guess_type
from django.contrib.auth import get_user_model
from slugify  import slugify

User = get_user_model()

class Upload(models.Model):
    source_url = models.URLField()
    final_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    thumbnail = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Upload: {self.title}"

    @property
    def downloads(self):
        return self.files.aggregate(models.Sum('downloads'))['downloads__sum'] or 0

class File(models.Model):
    class Type(models.TextChoices):
        VIDEO = 'video', 'Video'
        IMAGE = 'image', 'Image'
        MUSIC = 'music', 'Music'

    upload = models.ForeignKey(Upload, related_name='files', on_delete=models.CASCADE)
    url = models.URLField(max_length=2000)
    type = models.CharField(max_length=10, choices=Type.choices)
    label = models.CharField(max_length=100)
    filename = models.CharField(max_length=255, blank=True)
    cookies = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    downloads = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.filename}"

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class MediaAsset(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = 'image', 'Image'
        VIDEO = 'video', 'Video'
        AUDIO = 'audio', 'Audio'

    file = models.FileField(upload_to='uploads/')
    type = models.CharField(max_length=10, choices=MediaType.choices)
    alt_text = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="media_assets")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type}: {self.file.name}"

    def save(self, *args, **kwargs):
        if not self.alt_text:
            self.alt_text = os.path.basename(self.file.name)

        if not self.type:
            mime_type, _ = guess_type(self.file.name)
            if mime_type:
                if mime_type.startswith("image"):
                    self.type = self.MediaType.IMAGE
                elif mime_type.startswith("video"):
                    self.type = self.MediaType.VIDEO
                elif mime_type.startswith("audio"):
                    self.type = self.MediaType.AUDIO
        super().save(*args, **kwargs)

    @property
    def url(self):
        return self.file.url

    def delete(self, *args, **kwargs):
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']


class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    content = HTMLField()
    thumbnails = models.ManyToManyField(MediaAsset, related_name='articles')
    views = models.PositiveIntegerField(default=0)
    show_toc = models.BooleanField(default=True)
    show_meta = models.BooleanField(default=True)
    allow_comments = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='articles')
    tags = models.ManyToManyField('Tag', blank=True, related_name='articles')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_tags(self):
        return self.tags.all()

    def get_absolute_url(self):
        return reverse('article', kwargs={'slug': self.slug})

    @property
    def thumbnail(self):
        first_thumb = self.thumbnails.first()
        if first_thumb:
            return first_thumb.url

        soup = BeautifulSoup(self.content or "", "html.parser")
        first_img = soup.find("img")
        if first_img and first_img.get("src"):
            return first_img["src"]

        return static('images/banner.png')

class PinnedArticle(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name='pinned')
    pinned_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of precedence. Smaller numbers will appear first.")
    note = models.CharField(max_length=255, blank=True, help_text="Internal notes if needed.")

    class Meta:
        ordering = ['order', '-pinned_at']

    def __str__(self):
        return f"Ghim: {self.article.title}"

class Page(models.Model):

    FORMAT_CHOICES = [
        ('html', 'HTML'),
        ('text', 'Plain Text'),
        ('json', 'JSON'),
        ('js', 'JavaScript'),
        ('xml', 'XML'),
        ('md', 'Markdown'),
        ('csv', 'CSV'),
        ('rss', 'RSS'),
        ('yaml', 'YAML'),
        ('ini', 'INI'),
        ('custom', 'Custom Text'),
    ]

    name = models.CharField(max_length=200, unique=True)
    path = models.CharField(max_length=255, unique=True)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='html')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')

class Comment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Chờ duyệt'
        APPROVED = 'approved', 'Đã duyệt'
        REJECTED = 'rejected', 'Từ chối'

    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    reject_reason = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    moderated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - '{self.article.title}'"

    def approve(self):
        self.status = self.Status.APPROVED
        self.reject_reason = ''
        self.moderated_at = timezone.now()
        self.save()

    def reject(self, reason):
        self.status = self.Status.REJECTED
        self.reject_reason = reason
        self.moderated_at = timezone.now()
        self.save()

class ScheduledTopic(models.Model):
    topic = models.CharField(max_length=255, unique=True)
    scheduled = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_generated = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-scheduled']

    def __str__(self):
        return f"{self.topic} (expected: {self.scheduled.strftime('%Y-%m-%d %H:%M')})"