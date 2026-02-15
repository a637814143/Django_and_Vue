from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0005_loginlog"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="store_name",
            field=models.CharField(
                max_length=140,
                blank=True,
                help_text="商家店铺名称",
            ),
        ),
    ]

