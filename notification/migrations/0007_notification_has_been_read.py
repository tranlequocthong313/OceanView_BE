# Generated by Django 5.0.4 on 2024-04-30 04:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0006_rename_notifier_notification_recipient_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="has_been_read",
            field=models.BooleanField(default=False, verbose_name="Đã đọc"),
        ),
    ]