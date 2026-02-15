from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from campus_store.accounts.permissions import RolePermission

from .models import WishRequest, WishTimelineEntry
from .serializers import WishRequestSerializer, WishTimelineSerializer


class WishRequestViewSet(viewsets.ModelViewSet):
    serializer_class = WishRequestSerializer
    permission_classes = [RolePermission]
    allowed_roles = ["CONSUMER", "MERCHANT", "ADMIN"]

    def get_queryset(self):
        user = self.request.user
        qs = WishRequest.objects.prefetch_related("timeline", "consumer", "merchant")
        if user.role == user.Role.CONSUMER:
            return qs.filter(consumer=user)
        if user.role == user.Role.MERCHANT:
            return qs.filter(Q(merchant=user) | Q(merchant__isnull=True))
        return qs

    def perform_create(self, serializer):
        serializer.save(status=WishRequest.Status.SUBMITTED)

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        wish = self.get_object()
        if request.user.role not in (request.user.Role.MERCHANT, request.user.Role.ADMIN):
            return Response({"detail": "无权认领"}, status=status.HTTP_403_FORBIDDEN)
        wish.merchant = request.user
        wish.status = WishRequest.Status.IN_PROGRESS
        wish.save(update_fields=["merchant", "status", "updated_at"])
        WishTimelineEntry.objects.create(
            wish=wish,
            author=request.user,
            message="商家已认领该定制请求。",
        )
        return Response(WishRequestSerializer(wish, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def timeline(self, request, pk=None):
        wish = self.get_object()
        serializer = WishTimelineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entry = WishTimelineEntry.objects.create(
            wish=wish,
            author=request.user,
            message=serializer.validated_data["message"],
        )
        return Response(WishTimelineSerializer(entry).data, status=status.HTTP_201_CREATED)
