# Generated by Django 5.0.4 on 2024-05-09 12:35

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("invoice", "0011_payment_onlinewallet_proofimage"),
    ]

    operations = [
        migrations.CreateModel(
            name="InvoiceCreator",
            fields=[],
            options={
                "verbose_name": "Tạo hóa đơn",
                "verbose_name_plural": "Tạo hóa đơn",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("invoice.invoice",),
        ),
    ]