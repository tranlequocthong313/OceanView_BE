# Generated by Django 5.0.4 on 2024-04-17 16:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0003_alter_personalinformation_email"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="personalinformation",
            options={
                "verbose_name": "Thông tin cá nhân",
                "verbose_name_plural": "Thông tin cá nhân",
            },
        ),
        migrations.AlterModelOptions(
            name="user",
            options={"verbose_name": "Người dùng", "verbose_name_plural": "Người dùng"},
        ),
    ]