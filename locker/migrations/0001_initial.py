# Generated by Django 5.0.4 on 2024-04-22 16:04

import cloudinary.models
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
            name="Item",
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
                ("name", models.CharField(max_length=50, verbose_name="Tên")),
                ("quantity", models.PositiveSmallIntegerField(verbose_name="Tên")),
                (
                    "image",
                    cloudinary.models.CloudinaryField(
                        blank=True, max_length=255, null=True, verbose_name="Ảnh"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("RECEIVED", "Đã nhận"),
                            ("NOT_RECEIVED", "Chưa nhận"),
                        ],
                        default="NOT_RECEIVED",
                        max_length=20,
                        verbose_name="Trạng thái",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Cư dân",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
