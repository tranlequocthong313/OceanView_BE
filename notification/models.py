from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from app.models import MyBaseModel
from notification.types import EntityType, MessageTarget
from user.models import User


class FCMToken(MyBaseModel):
    class DeviceType(models.TextChoices):
        WEB = "WEB"
        ANDROID = "ANDROID"

    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    token = models.CharField(
        max_length=163, unique=True, validators=[MinLengthValidator(163)]
    )
    device_type = models.CharField(max_length=10, choices=DeviceType.choices)

    def __str__(self) -> str:
        return f"{self.user.__str__()} - {self.device_type}"


class NotificationContent(MyBaseModel):
    image = models.CharField(
        verbose_name=_("Ảnh"),
        null=True,
        blank=True,
        max_length=200,
    )
    entity_type = models.CharField(
        verbose_name=_("Loại thông báo"), choices=EntityType.choices, max_length=100
    )
    entity_id = models.CharField(verbose_name=_("Mã thực thể"), max_length=100)

    class Meta:
        verbose_name = _("Nội dung thông báo")
        verbose_name_plural = _("Nội dung thông báo")

    def __str__(self) -> str:
        return f"{self.get_entity_type_display()} - {self.entity_id}"


class NotificationSender(MyBaseModel):
    content = models.ForeignKey(
        verbose_name=_("Thông báo"),
        to=NotificationContent,
        on_delete=models.DO_NOTHING,
        db_index=True,
    )
    sender = models.ForeignKey(
        verbose_name=_("Người gửi"), to=User, on_delete=models.DO_NOTHING, db_index=True
    )

    class Meta:
        verbose_name = _("Người gửi thông báo")
        verbose_name_plural = _("Người gửi thông báo")

    def __str__(self) -> str:
        return self.sender.__str__()


class Notification(MyBaseModel):
    content = models.ForeignKey(
        verbose_name=_("Thông báo"),
        to=NotificationContent,
        on_delete=models.DO_NOTHING,
        db_index=True,
    )
    recipient = models.ForeignKey(
        verbose_name=_("Người nhận"),
        to=User,
        on_delete=models.DO_NOTHING,
        db_index=True,
    )
    has_been_read = models.BooleanField(verbose_name=_("Đã đọc"), default=False)
    target = models.CharField(
        verbose_name=_("Đối tượng"),
        choices=MessageTarget.choices,
        max_length=50,
        default=MessageTarget.ADMIN,
    )

    class Meta:
        verbose_name = _("Thông báo")
        verbose_name_plural = _("Thông báo")

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        if is_new:
            if self.target == MessageTarget.ADMIN:
                self.recipient.staff_unread_notifications += 1
            else:
                self.recipient.unread_notifications += 1
            self.recipient.save()

    def read(self):
        self.has_been_read = True
        if (
            self.recipient.unread_notifications > 0
            or self.recipient.staff_unread_notifications > 0
        ):
            if self.target == MessageTarget.ADMIN:
                self.recipient.staff_unread_notifications -= 1
            else:
                self.recipient.unread_notifications -= 1
            self.recipient.save()
        self.save()
        return True

    def __str__(self) -> str:
        return f"{self.recipient.__str__()} - {self.content.__str__()}"
