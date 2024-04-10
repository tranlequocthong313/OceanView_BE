# Generated by Django 5.0.4 on 2024-04-08 14:24

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
            name='InvoiceType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')),
                ('name', models.CharField(max_length=50, verbose_name='Tên loại hóa đơn')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')),
                ('id', models.CharField(max_length=10, primary_key=True, serialize=False, verbose_name='Mã hóa đơn')),
                ('payment_method', models.CharField(choices=[('E', 'Ví điện tử'), ('A', 'Ủy nhiệm chi')], max_length=1, verbose_name='Phương thức thanh toán')),
                ('total', models.DecimalField(decimal_places=2, max_digits=11, validators=[django.core.validators.MinLengthValidator(0)], verbose_name='Tổng cộng')),
                ('paid', models.DecimalField(decimal_places=2, max_digits=11, validators=[django.core.validators.MinLengthValidator(0)], verbose_name='Đã trả')),
                ('trading_code', models.CharField(max_length=50, null=True, verbose_name='Mã giao dịch')),
                ('payer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Giao dịch bởi')),
                ('invoice_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='invoice.invoicetype', verbose_name='Loại hóa đơn')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
