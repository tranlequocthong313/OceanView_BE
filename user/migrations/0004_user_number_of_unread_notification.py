# Generated by Django 5.0.4 on 2024-04-30 05:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0003_remove_user_locker_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="number_of_unread_notification",
            field=models.PositiveBigIntegerField(default=0),
            preserve_default=False,
        ),
    ]
