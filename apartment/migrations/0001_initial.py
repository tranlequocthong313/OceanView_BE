# Generated by Django 5.0.4 on 2024-04-08 14:23

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
            name='ApartmentBuilding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')),
                ('name', models.CharField(max_length=50, verbose_name='Tên chung cư')),
                ('address', models.CharField(max_length=50, verbose_name='Địa chỉ')),
                ('owner', models.CharField(max_length=50, verbose_name='Chủ sở hữu')),
                ('phone_number', models.CharField(max_length=11, validators=[django.core.validators.MinValueValidator(10)], verbose_name='Số điện thoại')),
                ('built_date', models.DateField(verbose_name='Năm xây dựng')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ApartmentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')),
                ('name', models.CharField(max_length=50, verbose_name='Tên loại căn hộ')),
                ('width', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Chiều rộng')),
                ('height', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Chiều dài')),
                ('number_of_bedroom', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Số phòng ngủ')),
                ('number_of_living_room', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Số phòng khách')),
                ('number_of_kitchen', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Số phòng bếp')),
                ('number_of_restroom', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Số nhà tắm')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')),
                ('name', models.CharField(max_length=10, verbose_name='Tên tòa nhà')),
                ('number_of_floors', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Số tầng')),
                ('apartment_building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apartment.apartmentbuilding', verbose_name='Chung cư')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Apartment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')),
                ('room_number', models.CharField(max_length=6, unique=True, verbose_name='Số phòng')),
                ('floor', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Tầng')),
                ('status', models.CharField(choices=[('E', 'Trống'), ('I', 'Có người ở'), ('A', 'Sắp chuyển đi')], default='E', max_length=1, verbose_name='Trạng thái')),
                ('residents', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, verbose_name='Danh sách cư dân')),
                ('apartment_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apartment.apartmenttype', verbose_name='Loại căn hộ')),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apartment.building', verbose_name='Tòa')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
