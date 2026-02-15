from django.contrib import admin

from .models import Category, Order, OrderItem, Product


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_available")
    list_filter = ("category", "is_available")
    search_fields = ("name",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "status", "created_at")
    list_filter = ("status",)
    inlines = [OrderItemInline]


admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
