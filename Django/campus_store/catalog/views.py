from django.contrib.auth import get_user_model
from rest_framework import filters, viewsets

from campus_store.accounts.permissions import RolePermission

from .models import Category, InventoryLog, Product
from .serializers import CategorySerializer, InventoryLogSerializer, ProductSerializer

User = get_user_model()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    allowed_roles = [User.Role.ADMIN, User.Role.MERCHANT]
    permission_classes = [RolePermission]


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "tags"]
    ordering_fields = ["created_at", "price", "inventory"]
    allowed_roles = [User.Role.ADMIN, User.Role.MERCHANT]
    permission_classes = [RolePermission]

    def get_queryset(self):
        queryset = Product.objects.select_related("category", "merchant")
        user = self.request.user
        if user.role == User.Role.MERCHANT:
            queryset = queryset.filter(merchant=user)
        return queryset


class InventoryLogViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryLogSerializer
    allowed_roles = [User.Role.ADMIN, User.Role.MERCHANT]
    permission_classes = [RolePermission]

    def get_queryset(self):
        user = self.request.user
        qs = InventoryLog.objects.select_related("product", "created_by", "product__merchant")
        if user.role == User.Role.MERCHANT:
            qs = qs.filter(product__merchant=user)
        return qs
