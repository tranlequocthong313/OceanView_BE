# Generated by Django 5.0.4 on 2024-05-09 14:34

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("invoice", "0012_invoicecreator"),
    ]

    operations = [
        migrations.DeleteModel(
            name="InvoiceCreator",
        ),
    ]
