from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Wallet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("balance", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="wallet",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="WalletConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "low_tier_limit",
                    models.DecimalField(decimal_places=2, default=Decimal("200.00"), max_digits=12),
                ),
                ("high_tier_requires_review", models.BooleanField(default=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="WalletTransaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "tx_type",
                    models.CharField(
                        choices=[("PAY", "支付"), ("REFUND", "退款"), ("ADJUST", "调账")], max_length=10
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("order_number", models.CharField(blank=True, max_length=32)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "wallet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transactions",
                        to="wallet.wallet",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
