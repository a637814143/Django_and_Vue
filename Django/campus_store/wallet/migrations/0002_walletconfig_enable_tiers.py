from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("wallet", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="walletconfig",
            name="enable_tiers",
            field=models.BooleanField(default=True),
        ),
    ]
