from django.contrib import admin

from .models import FocusVideo, FocusVideoComment, FocusVideoLike


@admin.register(FocusVideo)
class FocusVideoAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "creator", "status", "like_count", "comment_count", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "creator__username")


@admin.register(FocusVideoComment)
class FocusVideoCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "video", "author", "created_at")
    search_fields = ("video__title", "author__username", "content")


@admin.register(FocusVideoLike)
class FocusVideoLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "video", "user", "created_at")
