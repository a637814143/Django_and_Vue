from django.contrib import admin

from .models import MetricSnapshot


@admin.register(MetricSnapshot)
class MetricSnapshotAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "captured_at")
    search_fields = ("key",)
