from django.contrib import admin
from .models import Article, Upload, File, PinnedArticle, Tag, Page

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
    prepopulated_fields = {"slug": ("title",)}

@admin.register(PinnedArticle)
class PinnedArticleAdmin(admin.ModelAdmin):
    list_display = ("article", "order", "pinned_at", "note")
    search_fields = ("article__title",)
    ordering = ("order",)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name']

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "format", "is_published", "updated_at")
    search_fields = ("name", "slug", "content")
    list_filter = ("format", "is_published", "updated_at")
    prepopulated_fields = {"slug": ("name",)}
