# Generated by Django 5.0.4 on 2024-04-09 03:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("service", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="receiveparkingcardpermission",
            name="license_plate",
            field=models.CharField(
                max_length=10,
                unique=True,
                validators=[django.core.validators.MinLengthValidator(6)],
                verbose_name="Biển số",
            ),
        ),
    ]
