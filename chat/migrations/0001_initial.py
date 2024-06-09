# Generated by Django 5.0.4 on 2024-06-08 06:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Inbox",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_date",
                    models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo"),
                ),
                (
                    "updated_date",
                    models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật"),
                ),
                (
                    "user_1",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inboxes_as_user_1",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Người dùng 1",
                    ),
                ),
                (
                    "user_2",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inboxes_as_user_2",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Người dùng 2",
                    ),
                ),
            ],
            options={
                "verbose_name": "Hộp thư đến",
                "verbose_name_plural": "Hộp thư đến",
                "ordering": ["-updated_date"],
            },
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_date",
                    models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo"),
                ),
                (
                    "updated_date",
                    models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật"),
                ),
                ("content", models.TextField(verbose_name="Nội dung")),
                (
                    "inbox",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="chat.inbox",
                        verbose_name="Hộp thư đến",
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Người gửi",
                    ),
                ),
            ],
            options={
                "verbose_name": "Tin nhắn",
                "verbose_name_plural": "Tin nhắn",
                "ordering": ["-created_date"],
            },
        ),
        migrations.AddField(
            model_name="inbox",
            name="last_message",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="inbox_last_message",
                to="chat.message",
                verbose_name="Tin nhắn cuối cùng",
            ),
        ),
    ]
