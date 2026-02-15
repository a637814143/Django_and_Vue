from django.conf import settings
from django.db import models


class Post(models.Model):
    class Visibility(models.TextChoices):
        PUBLIC = "PUBLIC", "公开"
        MERCHANT = "MERCHANT", "商家可见"
        INTERNAL = "INTERNAL", "仅管理员"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="posts", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=180)
    content = models.TextField()
    cover_image = models.URLField(blank=True)
    visibility = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.PUBLIC)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class PostMedia(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = "IMAGE", "图片"
        VIDEO = "VIDEO", "视频"

    post = models.ForeignKey(Post, related_name="media_files", on_delete=models.CASCADE)
    file = models.FileField(upload_to="community_media/")
    media_type = models.CharField(max_length=10, choices=MediaType.choices, default=MediaType.IMAGE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.post_id} - {self.file.name}"


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="comments", on_delete=models.CASCADE
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class Reaction(models.Model):
    TYPES = [
        ("LIKE", "喜欢"),
        ("WOW", "惊叹"),
        ("IDEA", "灵感"),
    ]
    post = models.ForeignKey(Post, related_name="reactions", on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="reactions", on_delete=models.CASCADE
    )
    reaction_type = models.CharField(max_length=16, choices=TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "author", "reaction_type")
