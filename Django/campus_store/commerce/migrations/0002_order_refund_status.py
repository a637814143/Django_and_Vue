from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("commerce", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="refund_status",
            field=models.CharField(
                choices=[
                    ("NONE", "无退款"),
                    ("REQUESTED", "已申请"),
                    ("APPROVED", "已同意"),
                    ("REJECTED", "已拒绝"),
                ],
                default="NONE",
                help_text="退款审批状态",
                max_length=20,
            ),
        ),
    ]
