from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from ckeditor.fields import RichTextField
from django.urls import reverse

class Upload(models.Model):
    source_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    thumbnail = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Upload: {self.title}"

class File(models.Model):
    upload = models.ForeignKey(Upload, related_name='files', on_delete=models.CASCADE)
    url = models.URLField()
    label = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.label} - {self.url}"

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    summary = models.CharField(max_length=255, blank=True)
    content = RichTextField()
    cover_image = models.URLField(blank=True, null=True)
    show_toc = models.BooleanField(default=True, help_text="Show list automatically if there is title?")
    show_meta = models.BooleanField(default=True, help_text="Enable if you want to display poster information and creation time")
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='articles')
    tags = models.ManyToManyField('Tag', blank=True, related_name='articles')

    class Meta:
        ordering = ['-published_at']

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
    ]

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='html')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} ({self.format})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/pages/{self.slug}/"
