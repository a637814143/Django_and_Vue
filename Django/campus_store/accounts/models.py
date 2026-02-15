import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "管理员"
        CONSUMER = "CONSUMER", "消费者"
        MERCHANT = "MERCHANT", "商家"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CONSUMER,
        help_text="系统角色决定可访问的业务板块",
    )
    headline = models.CharField(max_length=140, blank=True)
    store_name = models.CharField(max_length=140, blank=True, help_text="商家店铺名称")
    avatar_url = models.URLField(blank=True)
    avatar_image = models.BinaryField(null=True, blank=True, editable=False)
    avatar_mime = models.CharField(max_length=120, blank=True, editable=False)

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN

    def __str__(self) -> str:
        return f"{self.username} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)


class SessionToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="session_tokens",
        on_delete=models.CASCADE,
    )
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    user_agent = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user.username} <{self.token[:8]}>"

    @classmethod
    def issue(cls, user, user_agent: str | None = None) -> "SessionToken":
        life_hours = getattr(settings, "SESSION_TOKEN_TTL_HOURS", 12)
        token = secrets.token_hex(32)
        expires_at = timezone.now() + timedelta(hours=life_hours)
        return cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at,
            user_agent=user_agent or "",
        )

    def mark_inactive(self) -> None:
        if not self.is_active:
            return
        self.is_active = False
        self.save(update_fields=["is_active"])

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at


class CommandLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="command_logs",
        on_delete=models.CASCADE,
    )
    command = models.TextField()
    output = models.TextField(blank=True)
    exit_code = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user.username} $ {self.command[:40]}"


class Address(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="addresses",
        on_delete=models.CASCADE,
    )
    receiver_name = models.CharField(max_length=64)
    phone = models.CharField(max_length=32)
    dorm_building = models.CharField(max_length=64, blank=True)
    dorm_room = models.CharField(max_length=64, blank=True)
    detail = models.CharField(max_length=255, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "-updated_at"]

    def __str__(self) -> str:
        return f"{self.receiver_name} {self.phone} {self.dorm_building} {self.dorm_room}"


class LoginLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="login_logs",
        on_delete=models.CASCADE,
    )
    user_agent = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user} @ {self.created_at:%Y-%m-%d %H:%M:%S}"
