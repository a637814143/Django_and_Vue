from decimal import Decimal
import secrets

from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from campus_store.accounts.permissions import RolePermission
from campus_store.catalog.models import Product
from campus_store.commerce.models import Order
from campus_store.commerce.serializers import OrderSerializer

from .models import WalletConfig
from .serializers import (
    WalletConfigSerializer,
    WalletOverviewSerializer,
    WalletPaySerializer,
    WalletRechargeSerializer,
    WalletRefundSerializer,
    VoucherSerializer,
    VoucherGenerateSerializer,
    VoucherRedeemSerializer,
    ensure_wallet,
    record_tx,
)


class WalletOverviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wallet = ensure_wallet(request.user)
        config = WalletConfig.get_solo()
        data = WalletOverviewSerializer(
            {
                "balance": wallet.balance,
                "tier": "LOW",
                "low_tier_limit": config.low_tier_limit,
                "pending_review": False,
                "enable_tiers": config.enable_tiers,
                "high_tier_requires_review": config.high_tier_requires_review,
            }
        ).data
        return Response(data)


class WalletPayView(APIView):
    permission_classes = [permissions.IsAuthenticated, RolePermission]
    allowed_roles = ["CONSUMER"]

    def post(self, request):
        serializer = WalletPaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = Decimal(serializer.validated_data["amount"])
        config = WalletConfig.get_solo()
        wallet = ensure_wallet(request.user)

        order = None
        order_items = []

        # Pay existing order
        if serializer.validated_data.get("order_id"):
            order = (
                Order.objects.filter(pk=serializer.validated_data["order_id"], consumer=request.user)
                .select_related("consumer")
                .first()
            )
            if not order:
                return Response({"detail": "订单不存在或不属于当前用户"}, status=status.HTTP_404_NOT_FOUND)
            if order.status != Order.Status.CREATED:
                return Response({"detail": "订单已支付或不可支付"}, status=status.HTTP_400_BAD_REQUEST)
            expected = order.total_amount
            amount = expected
        else:
            # Create new order based on cart items and backend price
            items_data = serializer.validated_data.get("items") or []
            subtotal = Decimal("0.00")
            merchant = None
            for item in items_data:
                product_id = item.get("product_id") or item.get("product")
                quantity = int(item.get("quantity") or 1)
                product = Product.objects.filter(pk=product_id, is_active=True).first()
                if not product:
                    return Response({"detail": f"商品 {product_id} 不存在"}, status=status.HTTP_400_BAD_REQUEST)
                merchant = merchant or product.merchant
                unit_price = product.price
                subtotal += unit_price * quantity
                order_items.append(
                    {
                        "product_id": product.id,
                        "quantity": quantity,
                        "custom_details": item.get("custom_details", ""),
                    }
                )

            expected = subtotal.quantize(Decimal("0.01"))
            if expected != amount.quantize(Decimal("0.01")):
                amount = expected  # trust backend calculation

        needs_review = (
            config.enable_tiers and config.high_tier_requires_review and amount > config.low_tier_limit
        )
        if not needs_review and wallet.balance < amount:
            return Response({"detail": "余额不足"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            if order is None:
                order_payload = {
                    "items": order_items,
                    "note": serializer.validated_data.get("note", ""),
                    "shipping_address": serializer.validated_data.get("shipping_address", ""),
                    "payment_method": "wallet",
                }
                order_serializer = OrderSerializer(data=order_payload, context={"request": request})
                order_serializer.is_valid(raise_exception=True)
                order: Order = order_serializer.save()

            order.payment_method = "wallet"
            if needs_review:
                order.status = Order.Status.CREATED
                order.save(update_fields=["status", "payment_method", "updated_at"])
                record_tx(wallet, "PAY", Decimal("0.00"), order.order_number, {"pending_review": True})
                return Response(
                    {
                        "status": "PENDING_REVIEW",
                        "pending_review": True,
                        "balance": wallet.balance,
                        "low_tier_limit": config.low_tier_limit,
                        "order_number": order.order_number,
                        "detail": "高档交易已提交审核，审核通过后再扣款",
                        "enable_tiers": config.enable_tiers,
                        "high_tier_requires_review": config.high_tier_requires_review,
                    },
                    status=status.HTTP_202_ACCEPTED,
                )

            wallet.adjust(-amount)
            order.status = Order.Status.PAID
            order.save(update_fields=["status", "payment_method", "updated_at"])
            record_tx(wallet, "PAY", -amount, order.order_number, {"auto": True})

        return Response(
            {
                "status": "PAID",
                "pending_review": False,
                "balance": wallet.balance,
                "low_tier_limit": config.low_tier_limit,
                "order_number": order.order_number,
                "detail": "支付成功，已从钱包扣款",
                "enable_tiers": config.enable_tiers,
                "high_tier_requires_review": config.high_tier_requires_review,
            }
        )


class WalletRefundView(APIView):
    permission_classes = [permissions.IsAuthenticated, RolePermission]
    allowed_roles = ["CONSUMER", "MERCHANT", "ADMIN"]

    def post(self, request):
        serializer = WalletRefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data.get("action") or "REQUEST"

        order = None
        if serializer.validated_data.get("order_id"):
            order = Order.objects.filter(pk=serializer.validated_data["order_id"]).first()
        if not order and serializer.validated_data.get("order_number"):
            order = Order.objects.filter(order_number=serializer.validated_data["order_number"]).first()
        if not order:
            return Response({"detail": "订单不存在"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        def apply_refund(target_order: Order, force=False):
            if target_order.status == Order.Status.CANCELLED and target_order.refund_status == Order.RefundStatus.APPROVED:
                return Response({"detail": "订单已退款"}, status=status.HTTP_400_BAD_REQUEST)
            if not force and target_order.status not in [
                Order.Status.PAID,
                Order.Status.SHIPPED,
                Order.Status.FULFILLED,
                Order.Status.COMPLETED,
            ]:
                return Response({"detail": "当前状态不可退款"}, status=status.HTTP_400_BAD_REQUEST)

            wallet = ensure_wallet(target_order.consumer)
            with transaction.atomic():
                refund_amount = target_order.total_amount
                wallet.adjust(refund_amount)
                target_order.status = Order.Status.CANCELLED
                target_order.refund_status = Order.RefundStatus.APPROVED
                target_order.save(update_fields=["status", "refund_status", "updated_at"])
                record_tx(wallet, "REFUND", refund_amount, target_order.order_number, {"source": "refund"})
            return Response({"detail": "退款已退回钱包", "balance": wallet.balance})

        # Consumer: only request
        if user.role == user.Role.CONSUMER:
            order.refund_status = Order.RefundStatus.REQUESTED
            order.save(update_fields=["refund_status", "updated_at"])
            return Response({"detail": "已提交退款申请，等待商家处理"}, status=status.HTTP_202_ACCEPTED)

        # Merchant actions
        if user.role == user.Role.MERCHANT:
            if order.merchant != user:
                return Response({"detail": "无权处理该订单退款"}, status=status.HTTP_403_FORBIDDEN)
            if action == "APPROVE":
                return apply_refund(order)
            if action == "REJECT":
                order.refund_status = Order.RefundStatus.REJECTED
                order.save(update_fields=["refund_status", "updated_at"])
                return Response({"detail": "已拒绝退款"}, status=status.HTTP_200_OK)
            return Response({"detail": "商家仅支持同意或拒绝"}, status=status.HTTP_400_BAD_REQUEST)

        # Admin: can force or approve/reject
        if user.role == user.Role.ADMIN:
            if action in ["FORCE", "APPROVE"]:
                return apply_refund(order, force=True)
            if action == "REJECT":
                order.refund_status = Order.RefundStatus.REJECTED
                order.save(update_fields=["refund_status", "updated_at"])
                return Response({"detail": "管理员已拒绝退款"}, status=status.HTTP_200_OK)
            # default fallback
            return apply_refund(order, force=True)

        return Response({"detail": "无权限"}, status=status.HTTP_403_FORBIDDEN)


class WalletConfigView(APIView):
    permission_classes = [permissions.IsAuthenticated, RolePermission]
    allowed_roles = ["ADMIN"]

    def get(self, request):
        config = WalletConfig.get_solo()
        return Response(WalletConfigSerializer(config).data)

    def put(self, request):
        config = WalletConfig.get_solo()
        serializer = WalletConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "配置已更新", **serializer.data})


class WalletRechargeView(APIView):
    permission_classes = [permissions.IsAuthenticated, RolePermission]
    allowed_roles = ["CONSUMER", "ADMIN"]

    def post(self, request):
        serializer = WalletRechargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data["amount"]
        if amount <= 0:
            return Response({"detail": "充值金额需大于 0"}, status=status.HTTP_400_BAD_REQUEST)
        wallet = ensure_wallet(request.user)
        with transaction.atomic():
            wallet.adjust(amount)
            record_tx(wallet, "ADJUST", amount, metadata={"source": "recharge"})
        return Response({"detail": "充值成功", "balance": wallet.balance})


class WalletVoucherGenerateView(APIView):
    permission_classes = [permissions.IsAuthenticated, RolePermission]
    allowed_roles = ["ADMIN"]

    def post(self, request):
        serializer = VoucherGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data["amount"]
        count = serializer.validated_data.get("count") or 1
        total_cost = amount * count

        wallet = ensure_wallet(request.user)
        if wallet.balance < total_cost:
            return Response({"detail": "管理员余额不足，无法生成兑换码"}, status=status.HTTP_400_BAD_REQUEST)

        codes = []
        from .models import WalletVoucher

        def gen_code():
            return secrets.token_urlsafe(8).upper().replace("-", "")[:12]

        with transaction.atomic():
            wallet.adjust(-total_cost)
            record_tx(wallet, "ADJUST", -total_cost, metadata={"source": "voucher_generate", "count": count})
            for _ in range(count):
                code = gen_code()
                while WalletVoucher.objects.filter(code=code).exists():
                    code = gen_code()
                voucher = WalletVoucher.objects.create(
                    code=code,
                    amount=amount,
                    created_by=request.user,
                )
                codes.append(VoucherSerializer(voucher).data)

        return Response({"detail": "生成成功", "balance": wallet.balance, "codes": codes})


class WalletVoucherRedeemView(APIView):
    permission_classes = [permissions.IsAuthenticated, RolePermission]
    allowed_roles = ["CONSUMER"]

    def post(self, request):
        serializer = VoucherRedeemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"]

        from .models import WalletVoucher

        voucher = WalletVoucher.objects.filter(code=code).first()
        if not voucher:
            return Response({"detail": "兑换码不存在"}, status=status.HTTP_404_NOT_FOUND)
        if voucher.is_redeemed:
            return Response({"detail": "兑换码已被使用"}, status=status.HTTP_400_BAD_REQUEST)

        wallet = ensure_wallet(request.user)
        with transaction.atomic():
            voucher.mark_redeemed(request.user)
            wallet.adjust(voucher.amount)
            record_tx(wallet, "ADJUST", voucher.amount, voucher.code, {"source": "voucher"})

        return Response({"detail": "兑换成功，已入账钱包", "balance": wallet.balance, "amount": voucher.amount})


class WalletVoucherListView(APIView):
    permission_classes = [permissions.IsAuthenticated, RolePermission]
    allowed_roles = ["ADMIN"]

    def get(self, request):
        from .models import WalletVoucher

        vouchers = WalletVoucher.objects.all().order_by("-created_at")[:200]
        return Response(VoucherSerializer(vouchers, many=True).data)
