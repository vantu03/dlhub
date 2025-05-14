from django.contrib import admin
from .models import Article, Upload, File

@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = ("title", "source_url", "created_at")
    search_fields = ("title", "source_url")

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("label", "url", "upload", "created_at")
    search_fields = ("label", "url")

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_at", "is_published")
    search_fields = ("title", "summary", "tags")
    list_filter = ("is_published", "published_at")
    prepopulated_fields = {"slug": ("title",)}  # tự điền slug từ title
