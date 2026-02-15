from datetime import timedelta

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from campus_store.accounts.permissions import RolePermission
from campus_store.catalog.models import Product

from .models import Order, PaymentIntent, Shipment
from .serializers import OrderSerializer, PaymentIntentSerializer, ShipmentSerializer


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [RolePermission]
    allowed_roles = ["CONSUMER", "MERCHANT", "ADMIN"]

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.prefetch_related("items__product", "consumer", "merchant")
        if user.role == user.Role.CONSUMER:
            return queryset.filter(consumer=user)
        if user.role == user.Role.MERCHANT:
            return queryset.filter(merchant=user)
        return queryset

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get("status")
        allowed = [choice[0] for choice in Order.Status.choices]
        if new_status not in allowed:
            return Response({"detail": "状态无效"}, status=status.HTTP_400_BAD_REQUEST)
        order.status = new_status
        order.save(update_fields=["status", "updated_at"])
        return Response(OrderSerializer(order, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def create_payment_intent(self, request, pk=None):
        order = self.get_object()
        if hasattr(order, "payment_intent"):
            serializer = PaymentIntentSerializer(order.payment_intent)
            return Response(serializer.data)
        expires_at = timezone.now() + timedelta(minutes=30)
        payment_intent = PaymentIntent.objects.create(
            order=order,
            provider="mock",
            reference=f"PI-{order.order_number}",
            amount=order.total_amount,
            expires_at=expires_at,
        )
        return Response(PaymentIntentSerializer(payment_intent).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        order = self.get_object()
        order.status = Order.Status.PAID
        order.save(update_fields=["status", "updated_at"])
        return Response(OrderSerializer(order, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def shipment(self, request, pk=None):
        order = self.get_object()
        shipment, _ = Shipment.objects.get_or_create(order=order)
        shipment.dispatch(
            tracking_number=request.data.get("tracking_number", ""),
            carrier=request.data.get("carrier", "校园速递"),
        )
        serializer = ShipmentSerializer(shipment)
        return Response(serializer.data)
