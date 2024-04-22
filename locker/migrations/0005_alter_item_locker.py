# Generated by Django 5.0.4 on 2024-04-22 16:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("locker", "0004_remove_item_user_locker_item_locker"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="locker",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="locker.locker",
                verbose_name="Tủ đồ",
            ),
        ),
    ]