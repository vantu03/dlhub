from django.contrib import admin
from .models import Article, Upload, File, PinnedArticle, Tag, Page, Comment, Favorite

@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = ("title", "source_url", "file_count", "created_at")
    search_fields = ("title", "source_url")

    def file_count(self, obj):
        return obj.files.count()
    file_count.short_description = "Số file"

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("label", "filename", "upload", "type", "download_count", "created_at")
    search_fields = ("label", "url")
    list_filter = ("created_at", "upload")

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_editable = ("is_published",)
    list_display = ("title", "author", "published_at", "is_published", "show_toc")
    search_fields = ("title", "summary", "tags")
    list_filter = ("is_published", "published_at")
    prepopulated_fields = {"slug": ("title",)}

    class Media:
        js = ('js/ckeditor-5.js',)

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

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "added_at")
    search_fields = ("user__username", "article__title")
    list_filter = ("added_at",)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "short_content", "status", "created_at", "moderated_at")
    list_filter = ("status", "created_at", "moderated_at")
    search_fields = ("user__username", "article__title", "content")
    readonly_fields = ("created_at", "moderated_at")

    actions = ["approve_comments", "reject_comments"]

    def short_content(self, obj):
        return (obj.content[:50] + "...") if len(obj.content) > 50 else obj.content
    short_content.short_description = "Nội dung"

    @admin.action(description="Duyệt các bình luận được chọn")
    def approve_comments(self, request, queryset):
        for comment in queryset:
            comment.approve()
        self.message_user(request, f"Đã duyệt {queryset.count()} bình luận.")

    @admin.action(description="Từ chối các bình luận (lý do trống)")
    def reject_comments(self, request, queryset):
        for comment in queryset:
            comment.reject("Từ chối bởi quản trị viên.")
        self.message_user(request, f"Đã từ chối {queryset.count()} bình luận.")