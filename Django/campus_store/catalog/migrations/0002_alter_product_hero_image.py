from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="hero_image",
            field=models.TextField(blank=True),
        ),
    ]
