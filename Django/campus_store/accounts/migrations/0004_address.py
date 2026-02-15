from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_user_avatar_image_user_avatar_mime"),
    ]

    operations = [
        migrations.CreateModel(
            name="Address",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("receiver_name", models.CharField(max_length=64)),
                ("phone", models.CharField(max_length=32)),
                ("dorm_building", models.CharField(blank=True, max_length=64)),
                ("dorm_room", models.CharField(blank=True, max_length=64)),
                ("detail", models.CharField(blank=True, max_length=255)),
                ("is_default", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="addresses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-is_default", "-updated_at"],
            },
        ),
    ]
