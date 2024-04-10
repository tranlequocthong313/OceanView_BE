from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db.models import (
    CASCADE,
    CharField,
    ForeignKey,
    OneToOneField,
    SmallIntegerField,
    TextChoices,
)
from django.utils.translation import gettext_lazy as _

from app.models import MyBaseModel
from user.models import PersonalInformation


class AccessPermission(MyBaseModel):
    class Status(TextChoices):
        WAITING_FOR_APPROVAL = "W", _("Chờ được xét duyệt")
        APPROVED = "A", _("Đã được duyệt")

    resident_registered = ForeignKey(
        verbose_name=_("Cư dân đăng ký"), to=get_user_model(), on_delete=CASCADE
    )
    registered_person = OneToOneField(
        verbose_name=_("Người thân"),
        to=PersonalInformation,
        on_delete=CASCADE,
        primary_key=True,
    )
    status = CharField(
        _("Trạng thái"),
        max_length=1,
        choices=Status,
        default=Status.WAITING_FOR_APPROVAL,
    )

    def __str__(self) -> str:
        return f"{self.registered_person.phone_number} - {self.status.label}"


class ReceiveParkingCardPermission(AccessPermission):
    class VehicleType(TextChoices):
        BYCYCLE = "B", _("Xe đạp")
        MOTORBIKE = "M", _("Xe máy")
        CAR = "C", _("Xe ô tô")

    license_plate = CharField(
        _("Biển số"), max_length=10, unique=True, validators=[MinLengthValidator(6)]
    )
    vehicle_type = CharField(_("Loại phương tiện"), max_length=1, choices=VehicleType)
    number_of_seats = SmallIntegerField(
        _("Số chỗ ngồi"), validators=[MinValueValidator(1)]
    )

    def __str__(self) -> str:
        return f"{super().__str__()} - {self.license_plate}"
