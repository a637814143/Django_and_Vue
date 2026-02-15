from decimal import Decimal

from rest_framework import serializers

from campus_store.commerce.models import Order

from .models import Wallet, WalletConfig, WalletTransaction, WalletVoucher


class WalletOverviewSerializer(serializers.Serializer):
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    tier = serializers.CharField()
    low_tier_limit = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending_review = serializers.BooleanField()
    enable_tiers = serializers.BooleanField()
    high_tier_requires_review = serializers.BooleanField()


class WalletConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletConfig
        fields = ["low_tier_limit", "high_tier_requires_review", "enable_tiers"]


class WalletRechargeSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)


class VoucherGenerateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    count = serializers.IntegerField(min_value=1, max_value=50, default=1)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("金额需大于 0")
        return value


class VoucherRedeemSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=24)


class VoucherSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    redeemed_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = WalletVoucher
        fields = ["code", "amount", "is_redeemed", "redeemed_at", "created_at", "created_by", "redeemed_by"]


class WalletPaySerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    items = serializers.ListField(child=serializers.DictField(), required=False, allow_empty=True)
    order_id = serializers.IntegerField(required=False)
    shipping_address = serializers.CharField(allow_blank=True, required=False)
    note = serializers.CharField(allow_blank=True, required=False)

    def validate(self, attrs):
        # If not paying an existing order, items are required
        if not attrs.get("order_id"):
            items = attrs.get("items") or []
            if len(items) == 0:
                raise serializers.ValidationError("需要提供商品明细或 order_id")
        return attrs


class WalletRefundSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=False)
    order_number = serializers.CharField(required=False)
    action = serializers.ChoiceField(
        choices=[("REQUEST", "REQUEST"), ("APPROVE", "APPROVE"), ("REJECT", "REJECT"), ("FORCE", "FORCE")],
        required=False,
    )

    def validate(self, attrs):
        if not attrs.get("order_id") and not attrs.get("order_number"):
            raise serializers.ValidationError("order_id 或 order_number 需提供一项")
        return attrs


def ensure_wallet(user):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    return wallet


def record_tx(wallet: Wallet, tx_type: str, amount: Decimal, order_number: str = "", metadata=None):
    WalletTransaction.objects.create(
        wallet=wallet,
        tx_type=tx_type,
        amount=Decimal(amount),
        order_number=order_number or "",
        metadata=metadata or {},
    )
