from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import CommandLog, SessionToken, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("角色信息", {"fields": ("role", "headline", "avatar_url")}),
    )
    list_display = ("username", "email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_staff", "is_active")


@admin.register(SessionToken)
class SessionTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "is_active", "expires_at", "user_agent")
    search_fields = ("token", "user__username")
    list_filter = ("is_active",)


@admin.register(CommandLog)
class CommandLogAdmin(admin.ModelAdmin):
    list_display = ("user", "command", "exit_code", "created_at")
    search_fields = ("command", "user__username")
    readonly_fields = ("user", "command", "output", "exit_code", "created_at")
