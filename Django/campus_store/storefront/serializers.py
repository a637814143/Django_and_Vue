from django.contrib.auth import get_user_model
from rest_framework import serializers

from campus_store.catalog.models import Category, Product

User = get_user_model()


class StorefrontProductBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "price", "hero_image"]
        read_only_fields = fields


class StorefrontProductSerializer(serializers.ModelSerializer):
    store = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "inventory",
            "hero_image",
            "tags",
            "store",
            "category",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_store(self, obj: Product):
        merchant = getattr(obj, "merchant", None)
        if not merchant:
            return None
        store_name = (merchant.store_name or "").strip() or merchant.username
        return {
            "id": merchant.id,
            "name": store_name,
            "description": merchant.headline,
            "avatar_url": merchant.avatar_url,
        }

    def get_category(self, obj: Product):
        category = getattr(obj, "category", None)
        if not category:
            return None
        return {"id": category.id, "name": category.name}


class StorefrontStoreSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.CharField(source="headline", read_only=True)
    product_count = serializers.IntegerField(read_only=True)
    preview_products = StorefrontProductBriefSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "name", "description", "avatar_url", "product_count", "preview_products"]
        read_only_fields = fields

    def get_name(self, obj):
        return (obj.store_name or "").strip() or obj.username


class StorefrontCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]
        read_only_fields = fields
