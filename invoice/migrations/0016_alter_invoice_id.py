# Generated by Django 5.0.4 on 2024-05-14 02:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("invoice", "0015_alter_invoice_total_amount_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invoice",
            name="id",
            field=models.CharField(
                blank=True,
                max_length=10,
                primary_key=True,
                serialize=False,
                verbose_name="Mã hóa đơn",
            ),
        ),
    ]
