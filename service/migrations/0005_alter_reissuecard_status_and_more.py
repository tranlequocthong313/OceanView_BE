# Generated by Django 5.0.4 on 2024-05-13 14:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("service", "0004_alter_serviceregistration_payment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reissuecard",
            name="status",
            field=models.CharField(
                choices=[
                    ("WAITING_FOR_APPROVAL", "Chờ được xét duyệt"),
                    ("APPROVED", "Đã được duyệt"),
                    ("REJECTED", "Bị từ chối"),
                    ("CANCELED", "Đã hủy"),
                ],
                default="WAITING_FOR_APPROVAL",
                max_length=30,
                verbose_name="Trạng thái",
            ),
        ),
        migrations.AlterField(
            model_name="serviceregistration",
            name="status",
            field=models.CharField(
                choices=[
                    ("WAITING_FOR_APPROVAL", "Chờ được xét duyệt"),
                    ("APPROVED", "Đã được duyệt"),
                    ("REJECTED", "Bị từ chối"),
                    ("CANCELED", "Đã hủy"),
                ],
                default="WAITING_FOR_APPROVAL",
                max_length=30,
                verbose_name="Trạng thái",
            ),
        ),
    ]
