from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from campus_store.accounts.permissions import RolePermission
from campus_store.accounts.models import LoginLog, SessionToken
from campus_store.catalog.models import Product
from campus_store.commerce.models import Order
from campus_store.customization.models import WishRequest
from campus_store.community.models import Comment
from campus_store.wallet.models import WalletTransaction

from .models import MetricSnapshot
from .serializers import MetricSerializer

User = get_user_model()


class MetricViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MetricSnapshot.objects.all()
    serializer_class = MetricSerializer
    permission_classes = [RolePermission]
    allowed_roles = [User.Role.ADMIN]


class AnalyticsOverviewView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = [User.Role.ADMIN, User.Role.MERCHANT]

    def get(self, request):
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        orders = Order.objects.filter(created_at__gte=week_ago)
        sales = orders.aggregate(total=Sum("total_amount")).get("total") or 0
        order_count = orders.count()
        new_custom_requests = WishRequest.objects.filter(created_at__gte=week_ago).count()
        active_products = Product.objects.filter(is_active=True).count()
        payload = {
            "sales_last_7_days": sales,
            "orders_last_7_days": order_count,
            "custom_requests_last_7_days": new_custom_requests,
            "active_products": active_products,
        }
        return Response(payload)


class CommerceInsightsView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = [User.Role.ADMIN]

    def get(self, request):
        today = timezone.localdate()
        start_date = today - timedelta(days=29)
        window_end = today
        revenue_orders = Order.objects.all()
        total_revenue = revenue_orders.aggregate(total=Sum("total_amount")).get("total") or 0
        merchant_count = User.objects.filter(role=User.Role.MERCHANT).count()
        product_count = Product.objects.filter(is_active=True).count()

        start_dt = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
        end_dt = timezone.make_aware(datetime.combine(window_end, datetime.max.time()))

        monthly_orders = revenue_orders.filter(created_at__range=(start_dt, end_dt))
        if not monthly_orders.exists():
            latest = revenue_orders.order_by("-created_at").values_list("created_at", flat=True).first()
            if latest:
                window_end = timezone.localdate(latest)
                start_date = window_end - timedelta(days=29)
                start_dt = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
                end_dt = timezone.make_aware(datetime.combine(window_end, datetime.max.time()))
                monthly_orders = revenue_orders.filter(created_at__range=(start_dt, end_dt))

        daily_map = {}
        for entry in monthly_orders.values("created_at", "total_amount"):
            day = timezone.localdate(entry["created_at"])
            daily_map[day] = daily_map.get(day, 0) + float(entry["total_amount"] or 0)
        monthly_sales = []
        for i in range(30):
            day = start_date + timedelta(days=i)
            amount = float(daily_map.get(day, 0) or 0)
            monthly_sales.append({"date": day.isoformat(), "amount": amount})

        merchant_sales_qs = (
            monthly_orders.values("merchant_id", "merchant__username", "merchant__store_name")
            .annotate(total=Sum("total_amount"))
            .order_by("-total")
        )
        merchant_sales = [
            {
                "merchant_id": entry["merchant_id"],
                "merchant": entry["merchant__store_name"] or entry["merchant__username"],
                "amount": float(entry["total"] or 0),
            }
            for entry in merchant_sales_qs
        ]

        payload = {
            "total_revenue": float(total_revenue or 0),
            "merchant_count": merchant_count,
            "product_count": product_count,
            "monthly_sales": monthly_sales,
            "merchant_sales": merchant_sales,
            "window_start": start_date.isoformat(),
            "window_end": window_end.isoformat(),
        }
        return Response(payload)


class UserStatsView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = [User.Role.ADMIN]

    def get(self, request):
        users = User.objects.all().order_by("id")

        data = []
        for user in users:
            data.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "login_count": LoginLog.objects.filter(user=user).count(),
                    "consumer_spend": Order.objects.filter(consumer=user).aggregate(s=Sum("total_amount"))["s"] or 0,
                    "merchant_sales": Order.objects.filter(merchant=user).aggregate(s=Sum("total_amount"))["s"] or 0,
                    "comment_count": Comment.objects.filter(author=user).count(),
                    "refund_count": WalletTransaction.objects.filter(
                        wallet__user=user, tx_type=WalletTransaction.Type.REFUND
                    ).count(),
                }
            )
        return Response(data)


class UserLogsView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = [User.Role.ADMIN]

    def get(self, request, user_id: int):
        user = User.objects.filter(pk=user_id).first()
        if not user:
            return Response({"detail": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        login_logs = LoginLog.objects.filter(user=user).values(
            "created_at",
            "ip_address",
            "user_agent",
        )
        sessions = SessionToken.objects.filter(user=user).values(
            "created_at",
            "expires_at",
            "is_active",
            "user_agent",
        )
        return Response(
            {
                "user": {"id": user.id, "username": user.username},
                "login_logs": list(login_logs),
                "sessions": list(sessions),
            }
        )
