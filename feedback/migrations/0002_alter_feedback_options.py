# Generated by Django 5.0.4 on 2024-04-22 17:43

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("feedback", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="feedback",
            options={"verbose_name": "Phản ánh", "verbose_name_plural": "Phản ánh"},
        ),
    ]