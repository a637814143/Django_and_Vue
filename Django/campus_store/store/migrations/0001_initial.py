from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=64, unique=True)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("customer_name", models.CharField(max_length=64)),
                ("contact", models.CharField(max_length=64)),
                ("note", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("pending", "待处理"), ("confirmed", "已确认"), ("completed", "已完成"), ("cancelled", "已取消")], default="pending", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=128)),
                ("description", models.TextField(blank=True)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("stock", models.PositiveIntegerField(default=0)),
                ("is_available", models.BooleanField(default=True)),
                ("cover_image", models.URLField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="products", to="store.category")),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="store.order")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="order_items", to="store.product")),
            ],
            options={"verbose_name": "订单明细", "verbose_name_plural": "订单明细"},
        ),
    ]
