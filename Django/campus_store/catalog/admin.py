from django.contrib import admin

from .models import Category, InventoryLog, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "merchant", "price", "inventory", "is_active")
    search_fields = ("title", "merchant__username")
    list_filter = ("is_active", "allow_customization", "category")


@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ("product", "change", "created_at", "created_by")
    search_fields = ("product__title",)
