from django.conf import settings
from django.db import models


class FocusVideo(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "正常"
        DISABLED = "DISABLED", "已下架"

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="focus_videos",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    video = models.FileField(upload_to="focus/videos/")
    cover_image = models.ImageField(upload_to="focus/covers/", blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} by {self.creator}"


class FocusVideoLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="focus_video_likes",
        on_delete=models.CASCADE,
    )
    video = models.ForeignKey(FocusVideo, related_name="likes", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "video")

    def __str__(self) -> str:
        return f"{self.user} ❤️ {self.video}"


class FocusVideoComment(models.Model):
    video = models.ForeignKey(
        FocusVideo,
        related_name="comments",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="focus_video_comments",
        on_delete=models.CASCADE,
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.author} on {self.video}"
