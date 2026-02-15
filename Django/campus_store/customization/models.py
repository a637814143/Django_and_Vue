from django.conf import settings
from django.db import models


class WishRequest(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "草稿"
        SUBMITTED = "SUBMITTED", "已提交"
        IN_PROGRESS = "IN_PROGRESS", "制作中"
        COMPLETED = "COMPLETED", "已完成"
        REJECTED = "REJECTED", "已驳回"

    title = models.CharField(max_length=180)
    description = models.TextField()
    consumer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="wish_requests",
        on_delete=models.CASCADE,
    )
    merchant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="wish_assignments",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    attachments = models.JSONField(default=list, blank=True)
    budget = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    due_date = models.DateField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class WishTimelineEntry(models.Model):
    wish = models.ForeignKey(WishRequest, related_name="timeline", on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="wish_notes",
        on_delete=models.CASCADE,
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.wish.title} - {self.author}"
