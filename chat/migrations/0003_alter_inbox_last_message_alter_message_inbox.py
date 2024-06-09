# Generated by Django 5.0.4 on 2024-06-08 07:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0002_alter_inbox_last_message_alter_message_inbox"),
    ]

    operations = [
        migrations.AlterField(
            model_name="inbox",
            name="last_message",
            field=models.TextField(default="ahihi", verbose_name="Tin nhắn cuối cùng"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="message",
            name="inbox",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="chat.inbox",
                verbose_name="Hộp thư đến",
            ),
            preserve_default=False,
        ),
    ]