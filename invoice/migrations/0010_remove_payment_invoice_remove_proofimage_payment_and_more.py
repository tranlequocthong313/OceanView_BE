# Generated by Django 5.0.4 on 2024-05-09 07:47

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("invoice", "0009_remove_onlinewallet_transaction_code"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="payment",
            name="invoice",
        ),
        migrations.RemoveField(
            model_name="proofimage",
            name="payment",
        ),
        migrations.CreateModel(
            name="StatsRevenue",
            fields=[],
            options={
                "verbose_name": "Thống kê doanh thu",
                "verbose_name_plural": "Thống kê doanh thu",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("invoice.invoice",),
        ),
        migrations.DeleteModel(
            name="OnlineWallet",
        ),
        migrations.DeleteModel(
            name="Payment",
        ),
        migrations.DeleteModel(
            name="ProofImage",
        ),
    ]
