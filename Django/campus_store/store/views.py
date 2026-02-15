from rest_framework import filters, viewsets

from .models import Category, Order, Product
from .serializers import CategorySerializer, OrderSerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description"]

    def get_queryset(self):
        queryset = Product.objects.select_related("category").all()
        category_id = self.request.query_params.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        available = self.request.query_params.get("available")
        if available in {"true", "1"}:
            queryset = queryset.filter(is_available=True)
        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related("items__product").all()
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["customer_name", "contact"]
