from django.contrib import admin

from .models import WishRequest, WishTimelineEntry


class WishTimelineInline(admin.TabularInline):
    model = WishTimelineEntry
    extra = 0


@admin.register(WishRequest)
class WishRequestAdmin(admin.ModelAdmin):
    list_display = ("title", "consumer", "merchant", "status", "budget", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "consumer__username", "merchant__username")
    inlines = [WishTimelineInline]
