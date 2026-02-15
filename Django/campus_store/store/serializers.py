from django.db import transaction
from rest_framework import serializers

from .models import Category, Order, OrderItem, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "stock",
            "is_available",
            "cover_image",
            "category",
            "category_name",
        ]
        read_only_fields = ["id", "category_name"]


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "unit_price",
            "subtotal",
        ]
        read_only_fields = ["id", "product_name", "subtotal"]
        extra_kwargs = {"unit_price": {"required": False}}

    def get_subtotal(self, obj: OrderItem):
        return obj.subtotal


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total_amount = serializers.DecimalField(
        source="total_amount", read_only=True, decimal_places=2, max_digits=10
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_name",
            "contact",
            "note",
            "status",
            "created_at",
            "items",
            "total_amount",
        ]
        read_only_fields = ["id", "created_at", "total_amount"]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("订单至少包含一个商品")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            self._sync_items(order, items_data)
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        with transaction.atomic():
            instance.save()
            if items_data is not None:
                self._restore_stock(instance)
                instance.items.all().delete()
                self._sync_items(instance, items_data)
        return instance

    def _sync_items(self, order: Order, items_data):
        for item in items_data:
            product: Product = item["product"]
            quantity = item.get("quantity", 1)
            if product.stock < quantity:
                raise serializers.ValidationError(f"{product.name} 库存不足")
            product.stock -= quantity
            product.save(update_fields=["stock"])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=item.get("unit_price") or product.price,
            )

    def _restore_stock(self, order: Order):
        for item in order.items.all():
            product = item.product
            product.stock += item.quantity
            product.save(update_fields=["stock"])
