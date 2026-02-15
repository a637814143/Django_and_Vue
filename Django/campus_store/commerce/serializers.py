from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import serializers

from campus_store.catalog.models import Product

from .models import Order, OrderItem, PaymentIntent, Shipment

User = get_user_model()


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        read_only=False,
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_id",
            "quantity",
            "unit_price",
            "custom_details",
        ]
        read_only_fields = ["unit_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    consumer = serializers.StringRelatedField(read_only=True)
    merchant = serializers.StringRelatedField(read_only=True)
    status = serializers.CharField(read_only=True)
    refund_status = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "consumer",
            "merchant",
            "status",
            "subtotal",
            "total_amount",
            "note",
            "shipping_address",
            "payment_method",
            "refund_status",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["subtotal", "total_amount", "order_number", "created_at", "updated_at"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        if not items_data:
            raise serializers.ValidationError("订单至少需要一条商品明细")
        request = self.context["request"]
        consumer = request.user
        first_product = items_data[0]["product"]
        validated_data["consumer"] = consumer
        validated_data["merchant"] = first_product.merchant
        order = Order.objects.create(**validated_data)
        subtotal = Decimal("0.00")
        for item in items_data:
            product: Product = item["product"]
            quantity = item["quantity"]
            unit_price = product.price
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                custom_details=item.get("custom_details", ""),
            )
            product.inventory = max(0, product.inventory - quantity)
            product.save(update_fields=["inventory", "updated_at"])
            subtotal += unit_price * quantity
        order.subtotal = subtotal
        order.total_amount = subtotal
        order.save(update_fields=["subtotal", "total_amount"])
        return order


class PaymentIntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentIntent
        fields = ["provider", "reference", "amount", "expires_at", "is_confirmed"]


class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ["tracking_number", "carrier", "dispatched_at", "delivered_at"]
