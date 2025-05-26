from django.db import models
from django.contrib.auth.models import User
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
    url = models.URLField(max_length=2000)
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
    views = models.PositiveIntegerField(default=0)
    cover_image = models.URLField(blank=True, null=True)
    show_toc = models.BooleanField(default=True)
    show_meta = models.BooleanField(default=True)
    allow_comments = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='articles')
    tags = models.ManyToManyField('Tag', blank=True, related_name='articles')

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        import dltik.utils
        if not self.slug:
            self.slug = dltik.utils.slugify(self.title)
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
        import dltik.utils
        if not self.slug:
            self.slug = dltik.utils.slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/pages/{self.slug}/"

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
