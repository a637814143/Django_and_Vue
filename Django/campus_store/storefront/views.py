from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, Q
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from campus_store.accounts.permissions import AuthenticatedOrRedirect
from campus_store.catalog.models import Category, Product

from .serializers import (
    StorefrontCategorySerializer,
    StorefrontProductSerializer,
    StorefrontStoreSerializer,
)

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class StorefrontStoreViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StorefrontStoreSerializer
    permission_classes = [AuthenticatedOrRedirect]
    filter_backends = [filters.SearchFilter]
    search_fields = ["username", "headline", "store_name"]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        preview_products = Product.objects.filter(is_active=True).order_by("-updated_at")
        return (
            User.objects.filter(role=User.Role.MERCHANT)
            .annotate(
                product_count=Count(
                    "merchant_products",
                    filter=Q(merchant_products__is_active=True),
                )
            )
            .prefetch_related(
                Prefetch(
                    "merchant_products",
                    queryset=preview_products[:3],
                    to_attr="preview_products",
                )
            )
            .order_by("id")
        )

    @action(detail=True, methods=["get"], url_path="products")
    def products(self, request, pk=None):
        store = self.get_object()
        products = Product.objects.select_related("category", "merchant").filter(
            merchant=store,
            is_active=True,
        )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(products, request, view=self)
        serializer = StorefrontProductSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class StorefrontCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StorefrontCategorySerializer
    permission_classes = [AuthenticatedOrRedirect]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    pagination_class = None

    def get_queryset(self):
        queryset = Category.objects.all().order_by("name")
        if self.request.query_params.get("has_products"):
            queryset = queryset.filter(products__is_active=True).distinct()
        return queryset


class StorefrontProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StorefrontProductSerializer
    permission_classes = [AuthenticatedOrRedirect]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "tags"]
    ordering_fields = ["created_at", "price", "inventory"]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Product.objects.select_related("category", "merchant").filter(is_active=True)
        store_id = self.request.query_params.get("store")
        category_id = self.request.query_params.get("category")
        if store_id:
            queryset = queryset.filter(merchant_id=store_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset
