# Generated by Django 5.0.4 on 2024-05-09 08:45

import cloudinary.models
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("invoice", "0010_remove_payment_invoice_remove_proofimage_payment_and_more"),
        ("vnpay", "0001_initial"),
    ]

    operations = [
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
                    "total_amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=11,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Số tiền",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("SUCCESS", "Thành công"),
                            ("CONFIRMING", "Đang xác nhận"),
                            ("INVALID", "Không hợp lệ"),
                        ],
                        default="CONFIRMING",
                        max_length=20,
                        verbose_name="Trạng thái",
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
                "verbose_name": "Thanh toán",
                "verbose_name_plural": "Thanh toán",
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
                    "vnpay_billing",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="vnpay.billing",
                        verbose_name="Thanh toán vnpay",
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
                "verbose_name": "Thanh toán qua ví điện tử",
                "verbose_name_plural": "Thanh toán qua ví điện tử",
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
                        max_length=255, verbose_name="Ảnh chứng từ thanh toán"
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
                "verbose_name": "Ảnh chứng minh",
                "verbose_name_plural": "Ảnh chứng minh",
                "abstract": False,
            },
        ),
    ]