from __future__ import annotations

from decimal import Decimal

from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    cover_image = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.category.name})"


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "待处理"),
        (STATUS_CONFIRMED, "已确认"),
        (STATUS_COMPLETED, "已完成"),
        (STATUS_CANCELLED, "已取消"),
    ]

    customer_name = models.CharField(max_length=64)
    contact = models.CharField(max_length=64)
    note = models.TextField(blank=True)
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.customer_name} - {self.get_status_display()}"

    @property
    def total_amount(self) -> Decimal:
        total = Decimal("0.00")
        for item in self.items.all():
            total += item.subtotal
        return total


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "订单明细"
        verbose_name_plural = "订单明细"

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity
