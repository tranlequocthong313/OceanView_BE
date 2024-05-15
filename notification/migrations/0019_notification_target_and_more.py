# Generated by Django 5.0.4 on 2024-05-14 05:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0018_alter_notificationcontent_entity_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="target",
            field=models.CharField(
                choices=[
                    ("ADMIN", "Ban quản trị"),
                    ("RESIDENT", "Cư dân"),
                    ("RESIDENTS", "Nhiều cư dân"),
                    ("ALL", "Tất cả"),
                ],
                default="ADMIN",
                max_length=50,
                verbose_name="Đối tượng",
            ),
        ),
        migrations.AlterField(
            model_name="notificationcontent",
            name="entity_type",
            field=models.CharField(
                choices=[
                    ("SERVICE_REGISTER", "Đăng ký dịch vụ"),
                    ("SERVICE_APPROVED", "Đã duyệt đăng ký"),
                    ("SERVICE_REJECTED", "Đã từ chối đăng ký"),
                    ("REISSUE_APPROVED", "Đã duyệt cấp lại"),
                    ("REISSUE_REJECTED", "Đã từ chối cấp lại"),
                    ("SERVICE_REISSUE", "Cấp lại"),
                    ("FEEDBACK_POST", "Đăng phản ánh"),
                    ("INVOICE_PROOF_IMAGE_PAYMENT", "Thanh toán"),
                    ("NEWS_POST", "Đăng tin tức"),
                    ("INVOICE_CREATE", "Nhận hóa đơn"),
                    ("LOCKER_ITEM_ADD", "Đã nhận giúp"),
                ],
                max_length=100,
                verbose_name="Loại thông báo",
            ),
        ),
    ]