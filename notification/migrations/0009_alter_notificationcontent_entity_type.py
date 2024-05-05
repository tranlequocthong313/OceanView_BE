# Generated by Django 5.0.4 on 2024-05-02 11:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0008_alter_notificationcontent_entity_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notificationcontent",
            name="entity_type",
            field=models.CharField(
                choices=[
                    ("SERVICE_REGISTER", "Đăng ký dịch vụ"),
                    ("SERVICE_REISSUE", "Cấp lại"),
                    ("FEEDBACK_POST", "Đăng phản ánh"),
                ],
                max_length=100,
                verbose_name="Loại thông báo",
            ),
        ),
    ]