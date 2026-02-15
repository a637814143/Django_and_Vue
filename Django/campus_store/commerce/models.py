import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from campus_store.catalog.models import Product


def generate_order_number() -> str:
    return uuid.uuid4().hex[:12].upper()


class Order(models.Model):
    class Status(models.TextChoices):
        CREATED = "CREATED", "待支付"
        PAID = "PAID", "已支付"
        FULFILLED = "FULFILLED", "备货中"
        SHIPPED = "SHIPPED", "已发货"
        COMPLETED = "COMPLETED", "已完成"
        CANCELLED = "CANCELLED", "已取消/退款"

    class RefundStatus(models.TextChoices):
        NONE = "NONE", "无退款"
        REQUESTED = "REQUESTED", "已申请"
        APPROVED = "APPROVED", "已同意"
        REJECTED = "REJECTED", "已拒绝"

    order_number = models.CharField(max_length=24, default=generate_order_number, unique=True)
    consumer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="orders", on_delete=models.CASCADE)
    merchant = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="merchant_orders", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    refund_status = models.CharField(
        max_length=20, choices=RefundStatus.choices, default=RefundStatus.NONE, help_text="退款审批状态"
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    note = models.TextField(blank=True)
    shipping_address = models.CharField(max_length=255, blank=True)
    payment_method = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.order_number}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    custom_details = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.product.title} x{self.quantity}"


class PaymentIntent(models.Model):
    order = models.OneToOneField(Order, related_name="payment_intent", on_delete=models.CASCADE)
    provider = models.CharField(max_length=32, default="mock")
    reference = models.CharField(max_length=64, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expires_at = models.DateTimeField()
    is_confirmed = models.BooleanField(default=False)

    def mark_confirmed(self):
        self.is_confirmed = True
        self.save(update_fields=["is_confirmed"])
        self.order.status = Order.Status.PAID
        self.order.save(update_fields=["status", "updated_at"])


class Shipment(models.Model):
    order = models.OneToOneField(Order, related_name="shipment", on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=64, blank=True)
    carrier = models.CharField(max_length=64, blank=True)
    dispatched_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def dispatch(self, tracking_number: str, carrier: str):
        self.tracking_number = tracking_number
        self.carrier = carrier
        self.dispatched_at = timezone.now()
        self.save(update_fields=["tracking_number", "carrier", "dispatched_at"])
