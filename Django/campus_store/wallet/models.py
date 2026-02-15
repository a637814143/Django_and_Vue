from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="wallet", on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} ¥{self.balance}"

    def adjust(self, amount: Decimal):
        self.balance = (self.balance or Decimal("0.00")) + Decimal(amount)
        self.save(update_fields=["balance", "updated_at"])


class WalletTransaction(models.Model):
    class Type(models.TextChoices):
        PAY = "PAY", "支付"
        REFUND = "REFUND", "退款"
        ADJUST = "ADJUST", "调账"

    wallet = models.ForeignKey(Wallet, related_name="transactions", on_delete=models.CASCADE)
    tx_type = models.CharField(max_length=10, choices=Type.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    order_number = models.CharField(max_length=32, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tx_type} {self.amount}"


class WalletConfig(models.Model):
    low_tier_limit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("200.00"))
    high_tier_requires_review = models.BooleanField(default=True)
    enable_tiers = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.pk = 1  # ensure singleton
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={"low_tier_limit": Decimal("200.00")})
        return obj


class WalletVoucher(models.Model):
    code = models.CharField(max_length=24, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_redeemed = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_vouchers",
        on_delete=models.CASCADE,
    )
    redeemed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="redeemed_vouchers",
        on_delete=models.SET_NULL,
    )
    redeemed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def mark_redeemed(self, user):
        self.is_redeemed = True
        self.redeemed_by = user
        self.redeemed_at = timezone.now()
        self.save(update_fields=["is_redeemed", "redeemed_by", "redeemed_at"])
