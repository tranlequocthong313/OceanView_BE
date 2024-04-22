from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from app.models import MyBaseModel


class Locker(MyBaseModel):
    class LockerStatus(models.TextChoices):
        EMPTY = "EMPTY", _("Trống")
        NOT_EMPTY = "NOT_EMPTY", _("Có đồ")

    owner = models.OneToOneField(
        verbose_name=_("Chủ sở hữu"), to=get_user_model(), on_delete=models.CASCADE
    )
    status = models.CharField(
        verbose_name=_("Trạng thái"),
        max_length=10,
        choices=LockerStatus.choices,
        default=LockerStatus.EMPTY,
    )

    class Meta:
        verbose_name = _("Tủ đồ")
        verbose_name_plural = _("Tủ đồ")

    def __str__(self) -> str:
        return self.owner.__str__()


@receiver(post_save, sender=get_user_model())
def create_locker(sender, instance, created, **kwargs):
    if created:
        Locker.objects.create(owner=instance)


class Item(MyBaseModel):
    class ItemStatus(models.TextChoices):
        RECEIVED = "RECEIVED", _("Đã nhận")
        NOT_RECEIVED = "NOT_RECEIVED", _("Chưa nhận")

    name = models.CharField(verbose_name=_("Tên"), max_length=50)
    quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Số lượng"), validators=[MinValueValidator(1)]
    )
    image = CloudinaryField(_("Ảnh"), null=True, blank=True)
    locker = models.ForeignKey(
        verbose_name=_("Tủ đồ"), to=Locker, on_delete=models.CASCADE
    )
    status = models.CharField(
        verbose_name=_("Trạng thái"),
        max_length=20,
        choices=ItemStatus.choices,
        default=ItemStatus.NOT_RECEIVED,
    )

    class Meta:
        verbose_name = _("Món hàng")
        verbose_name_plural = _("Món hàng")

    def __str__(self) -> str:
        return self.name


@receiver(post_save, sender=Item)
@receiver(post_delete, sender=Item)
def update_locker_status(sender, instance, **kwargs):
    locker = instance.locker
    not_received_count = locker.item_set.filter(
        status=Item.ItemStatus.NOT_RECEIVED
    ).count()

    if not_received_count > 0:
        locker.status = Locker.LockerStatus.NOT_EMPTY
    else:
        locker.status = Locker.LockerStatus.EMPTY

    locker.save()
