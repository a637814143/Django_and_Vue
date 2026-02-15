from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_categories",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    merchant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="merchant_products",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory = models.PositiveIntegerField(default=0)
    allow_customization = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    hero_image = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title


class InventoryLog(models.Model):
    product = models.ForeignKey(Product, related_name="inventory_logs", on_delete=models.CASCADE)
    change = models.IntegerField()
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="inventory_actions",
    )

    class Meta:
        ordering = ["-created_at"]

    def apply(self):
        self.product.inventory = max(0, self.product.inventory + self.change)
        self.product.last_synced_at = timezone.now()
        self.product.save(update_fields=["inventory", "last_synced_at", "updated_at"])
