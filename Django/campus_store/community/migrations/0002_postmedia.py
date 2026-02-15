from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("community", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PostMedia",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to="community_media/")),
                (
                    "media_type",
                    models.CharField(
                        choices=[("IMAGE", "图片"), ("VIDEO", "视频")],
                        default="IMAGE",
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="media_files",
                        to="community.post",
                    ),
                ),
            ],
            options={
                "ordering": ["created_at"],
            },
        ),
    ]

