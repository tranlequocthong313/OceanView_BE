# Generated by Django 5.0.4 on 2024-05-04 13:33

import cloudinary.models
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("service", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Invoice",
            fields=[
                (
                    "created_date",
                    models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo"),
                ),
                (
                    "updated_date",
                    models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật"),
                ),
                (
                    "deleted",
                    models.BooleanField(default=False, verbose_name="Đã bị xóa"),
                ),
                (
                    "id",
                    models.CharField(
                        max_length=10,
                        primary_key=True,
                        serialize=False,
                        verbose_name="Mã hóa đơn",
                    ),
                ),
                (
                    "total_amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=11,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Số tiền",
                    ),
                ),
                ("due_date", models.DateField(verbose_name="Ngày đáo hạn")),
                (
                    "resident",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Cư dân",
                    ),
                ),
            ],
            options={
                "verbose_name": "Hóa đơn",
                "verbose_name_plural": "Hóa đơn",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="InvoiceDetail",
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
                    "deleted",
                    models.BooleanField(default=False, verbose_name="Đã bị xóa"),
                ),
                (
                    "invoice",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="invoice.invoice",
                        verbose_name="Hóa đơn",
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="service.service",
                        verbose_name="Dịch vụ",
                    ),
                ),
            ],
            options={
                "verbose_name": "Chi tiết hóa đơn",
                "verbose_name_plural": "Chi tiết hóa đơn",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Payment",
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
                    "deleted",
                    models.BooleanField(default=False, verbose_name="Đã bị xóa"),
                ),
                (
                    "method",
                    models.CharField(
                        choices=[
                            ("E_WALLET", "Ví điện tử"),
                            ("PROOF_IMAGE", "Ủy nhiệm chi"),
                        ],
                        max_length=15,
                        verbose_name="Phương thức thanh toán",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Chờ thanh toán"),
                            ("PAID", "Đã thanh toán"),
                            ("OVERDUE", "Quá hạn"),
                        ],
                        default="PENDING",
                        max_length=10,
                        verbose_name="Trạng thái thanh toán",
                    ),
                ),
                (
                    "total_amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=11,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Số tiền",
                    ),
                ),
                (
                    "invoice",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="invoice.invoice",
                        verbose_name="Hóa đơn",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="OnlineWallet",
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
                    "deleted",
                    models.BooleanField(default=False, verbose_name="Đã bị xóa"),
                ),
                (
                    "transaction_code",
                    models.CharField(
                        blank=True,
                        max_length=49,
                        null=True,
                        verbose_name="Mã giao dịch",
                    ),
                ),
                (
                    "payment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="invoice.payment",
                        verbose_name="Thanh toán",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ProofImage",
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
                    "deleted",
                    models.BooleanField(default=False, verbose_name="Đã bị xóa"),
                ),
                (
                    "image",
                    cloudinary.models.CloudinaryField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Ảnh chứng từ thanh toán",
                    ),
                ),
                (
                    "payment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="invoice.payment",
                        verbose_name="Thanh toán",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
