# Generated by Django 5.0.4 on 2024-05-08 15:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="news",
            name="is_broadcast",
            field=models.BooleanField(default=False, verbose_name="Gửi thông báo"),
        ),
    ]
