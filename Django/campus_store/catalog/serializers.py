from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Category, InventoryLog, Product

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "description", "created_at", "created_by"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["created_by"] = request.user
        return super().create(validated_data)


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )
    merchant = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "inventory",
            "allow_customization",
            "is_active",
            "hero_image",
            "tags",
            "category",
            "category_id",
            "merchant",
            "last_synced_at",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["merchant"] = request.user
        return super().create(validated_data)


class InventoryLogSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = InventoryLog
        fields = ["id", "product", "product_id", "change", "note", "created_at"]

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["created_by"] = request.user
        log = super().create(validated_data)
        log.apply()
        return log
