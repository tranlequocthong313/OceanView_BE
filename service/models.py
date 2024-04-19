from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db.models import (
    CASCADE,
    CharField,
    DecimalField,
    ForeignKey,
    ManyToManyField,
    OneToOneField,
    TextChoices,
)
from django.utils.translation import gettext_lazy as _

from apartment.models import Apartment
from app.models import MyBaseModel
from user.models import PersonalInformation


class Service(MyBaseModel):
    class ServiceType(TextChoices):
        ACCESS_CARD = "001", _("Thẻ ra vào")
        RESIDENT_CARD = "002", _("Thẻ cư dân")
        BYCYCLE_PARKING_CARD = "003", _("Thẻ gửi xe đạp")
        MOTOR_PARKING_CARD = "004", _("Thẻ gửi xe máy")
        CAR_PARKING_CARD = "005", _("Thẻ gửi xe ô tô")

    service_id = CharField(
        verbose_name=_("Mã dịch vụ"),
        primary_key=True,
        max_length=3,
        choices=ServiceType,
    )
    name = CharField(verbose_name=_("Tên dịch vụ"), max_length=50)
    price = DecimalField(
        _("Giá"),
        max_digits=11,
        decimal_places=0,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = _("Dịch vụ")
        verbose_name_plural = _("Dịch vụ")

    def __str__(self) -> str:
        return self.name


class Relative(MyBaseModel):
    relationship = CharField(
        verbose_name=_("Mối quan hệ"), max_length=20, null=True, blank=True
    )
    personal_information = OneToOneField(
        verbose_name=_("Thông tin cá nhân"),
        to=PersonalInformation,
        on_delete=CASCADE,
    )
    residents = ManyToManyField(verbose_name=_("Danh sách cư dân"), to=get_user_model())

    class Meta:
        verbose_name = _("Người thân")
        verbose_name_plural = _("Người thân")

    def __str__(self) -> str:
        return self.personal_information.__str__()


class ServiceRegistration(MyBaseModel):
    class Status(TextChoices):
        WAITING_FOR_APPROVAL = "W", _("Chờ được xét duyệt")
        APPROVED = "A", _("Đã được duyệt")

    service = ForeignKey(
        verbose_name=_("Dịch vụ"),
        to=Service,
        on_delete=CASCADE,
    )
    personal_information = ForeignKey(
        verbose_name=_("Người sử dụng dịch vụ"),
        to=PersonalInformation,
        on_delete=CASCADE,
    )
    resident = ForeignKey(
        verbose_name=_("Cư dân đăng ký"), to=get_user_model(), on_delete=CASCADE
    )
    status = CharField(
        _("Trạng thái"),
        max_length=1,
        choices=Status,
        default=Status.WAITING_FOR_APPROVAL,
    )

    class Meta:
        verbose_name = _("Đăng ký dịch vụ")
        verbose_name_plural = _("Đăng ký dịch vụ")

    def get_status_label(self):
        return dict(ServiceRegistration.Status.choices)[self.status]

    def __str__(self) -> str:
        return f"{self.personal_information} {self.service} - {self.get_status_label()}"


class VehicleInformation(MyBaseModel):
    class VehicleType(TextChoices):
        BYCYCLE = "B", _("Xe đạp")
        MOTORBIKE = "M", _("Xe máy")
        CAR = "C", _("Xe ô tô")

    license_plate = CharField(
        _("Biển số"),
        max_length=10,
        unique=True,
        validators=[MinLengthValidator(6)],
        null=True,
        blank=True,
    )
    vehicle_type = CharField(_("Loại phương tiện"), max_length=1, choices=VehicleType)
    service_registration = OneToOneField(
        verbose_name=_("Dịch vụ đăng ký"), to=ServiceRegistration, on_delete=CASCADE
    )
    apartment = ForeignKey(verbose_name=_("Căn hộ"), to=Apartment, on_delete=CASCADE)

    class Meta:
        verbose_name = _("Thông tin phương tiện")
        verbose_name_plural = _("Thông tin phương tiện")

    @classmethod
    def get_vehicle_type_label(cls, vehicle_type):
        return dict(cls.VehicleType.choices)[vehicle_type]

    def __str__(self) -> str:
        return f"{self.apartment} - {VehicleInformation.get_vehicle_type_label(self.vehicle_type)} - {self.license_plate if self.license_plate else ''}"

    @classmethod
    def get_service_id(cls, vehicle_type):
        SERVICE_IDS = {
            cls.VehicleType.BYCYCLE: Service.ServiceType.BYCYCLE_PARKING_CARD,
            cls.VehicleType.MOTORBIKE: Service.ServiceType.MOTOR_PARKING_CARD,
            cls.VehicleType.CAR: Service.ServiceType.CAR_PARKING_CARD,
        }
        return SERVICE_IDS[vehicle_type]
