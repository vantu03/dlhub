from django.contrib import admin
from .models import Article, Upload, File, PinnedArticle, Tag, Page, Comment, Favorite, MediaAsset, ScheduledTopic, SystemLog
from django.utils.html import format_html

@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = ("title", "files", "downloads", "source_url", "created_at")
    search_fields = ("title", "source_url")

    def files(self, obj):
        return obj.files.count()
    files.short_description = "Số file"


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("label", "filename", "upload", "type", "downloads", "created_at")
    search_fields = ("label", "url")
    list_filter = ("created_at", "upload")

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_editable = ("is_published",)
    list_display = ("title", "author", "created_at", "is_published", "show_toc")
    search_fields = ("title", "description", "tags")
    list_filter = ("is_published", "created_at")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ['thumbnails', 'tags']

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
    list_display = ("name", "path", "format", "is_published", "updated_at")
    search_fields = ("name", "path", "content")
    list_filter = ("format", "is_published", "updated_at")
    prepopulated_fields = {"path": ("name",)}

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


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ('type', 'alt_text', 'uploaded_by', 'preview', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ['alt_text', 'file']
    readonly_fields = ['created_at']

    def preview(self, obj):
        if obj.type == 'image' and obj.file:
            return format_html('<img src="{}" width="100" alt="{}" />', obj.file.url, obj.alt_text)
        return "Không hiển thị"

    preview.short_description = "Xem trước"

@admin.register(ScheduledTopic)
class ScheduledTopicAdmin(admin.ModelAdmin):
    list_display = ('topic', 'scheduled', 'author', 'is_generated', 'created_at')
    list_filter = ('is_generated', 'scheduled', 'author')
    search_fields = ('topic', 'author__username')
    readonly_fields = ('created_at',)

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "level", "source", "short_message")
    list_filter = ("level", "source")
    search_fields = ("message",)

    def short_message(self, obj):
        return (obj.message[:60] + "...") if len(obj.message) > 60 else obj.message