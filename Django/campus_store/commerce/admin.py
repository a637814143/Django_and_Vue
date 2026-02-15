from django.contrib import admin

from .models import Order, OrderItem, PaymentIntent, Shipment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "consumer", "merchant", "status", "total_amount", "created_at")
    list_filter = ("status",)
    search_fields = ("order_number", "consumer__username", "merchant__username")
    inlines = [OrderItemInline]


@admin.register(PaymentIntent)
class PaymentIntentAdmin(admin.ModelAdmin):
    list_display = ("order", "provider", "reference", "amount", "is_confirmed")


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("order", "tracking_number", "carrier", "dispatched_at", "delivered_at")
