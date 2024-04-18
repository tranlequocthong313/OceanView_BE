# Generated by Django 5.0.4 on 2024-04-17 16:48

import cloudinary.models
import django.core.validators
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
            name="InvoiceType",
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
                    "invoice_type_id",
                    models.CharField(
                        choices=[
                            ("ELECTRIC", "Điện"),
                            ("WATER", "Nước"),
                            ("INTERNET", "Internet"),
                            ("PARKING_CARD_SERVICE", "Dịch vụ gửi xe"),
                        ],
                        max_length=30,
                        primary_key=True,
                        serialize=False,
                        verbose_name="Mã loại hóa đơn",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=50, verbose_name="Tên loại hóa đơn"),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="Mô tả"
                    ),
                ),
            ],
            options={
                "verbose_name": "Loại hóa đơn",
                "verbose_name_plural": "Loại hóa đơn",
            },
        ),
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
                    "id",
                    models.CharField(
                        max_length=10,
                        primary_key=True,
                        serialize=False,
                        verbose_name="Mã hóa đơn",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=11,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Số tiền",
                    ),
                ),
                ("due_date", models.DateField(verbose_name="Ngày đáo hạn")),
                (
                    "payment_status",
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
                    "resident",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Cư dân",
                    ),
                ),
                (
                    "invoice_type",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="invoice.invoicetype",
                        verbose_name="Loại hóa đơn",
                    ),
                ),
            ],
            options={
                "verbose_name": "Hóa đơn",
                "verbose_name_plural": "Hóa đơn",
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
                    "payment_method",
                    models.CharField(
                        choices=[
                            ("E_WALLET", "Ví điện tử"),
                            ("ACCREDITATIVE", "Ủy nhiệm chi"),
                        ],
                        max_length=14,
                        verbose_name="Phương thức thanh toán",
                    ),
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
                    "payment_proof",
                    cloudinary.models.CloudinaryField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Ảnh chứng từ thanh toán",
                    ),
                ),
                (
                    "invoice",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="invoice.invoice",
                        verbose_name="Hóa đơn",
                    ),
                ),
            ],
            options={
                "verbose_name": "Chi tiết hóa đơn",
                "verbose_name_plural": "Chi tiết hóa đơn",
            },
        ),
    ]
