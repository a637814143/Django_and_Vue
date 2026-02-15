from django.contrib import admin

from .models import Comment, Post, Reaction


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "visibility", "created_at")
    list_filter = ("visibility",)
    search_fields = ("title", "author__username")
    inlines = [CommentInline]


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "reaction_type", "created_at")
