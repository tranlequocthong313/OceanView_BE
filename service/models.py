from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apartment.models import Apartment
from app.models import MyBaseModel
from user.models import PersonalInformation


class Service(MyBaseModel):
    class ServiceType(models.TextChoices):
        ACCESS_CARD = "ACCESS_CARD", _("Thẻ ra vào")
        RESIDENT_CARD = "RESIDENT_CARD", _("Thẻ cư dân")
        BYCYCLE_PARKING_CARD = "BYCYCLE_PARKING_CARD", _("Thẻ gửi xe đạp")
        MOTOR_PARKING_CARD = "MOTOR_PARKING_CARD", _("Thẻ gửi xe máy")
        CAR_PARKING_CARD = "CAR_PARKING_CARD", _("Thẻ gửi xe ô tô")

    service_id = models.CharField(
        verbose_name=_("Mã dịch vụ"),
        primary_key=True,
        max_length=30,
        choices=ServiceType.choices,
    )
    name = models.CharField(verbose_name=_("Tên dịch vụ"), max_length=50)
    price = models.DecimalField(
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
    relationship = models.CharField(
        verbose_name=_("Mối quan hệ"), max_length=20, null=True, blank=True
    )
    personal_information = models.OneToOneField(
        verbose_name=_("Thông tin cá nhân"),
        to=PersonalInformation,
        on_delete=models.CASCADE,
    )
    residents = models.ManyToManyField(
        verbose_name=_("Danh sách cư dân"), to=get_user_model()
    )

    class Meta:
        verbose_name = _("Người thân")
        verbose_name_plural = _("Người thân")

    def __str__(self) -> str:
        return self.personal_information.__str__()


class ServiceRegistration(MyBaseModel):
    class Status(models.TextChoices):
        WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL", _("Chờ được xét duyệt")
        APPROVED = "APPROVED", _("Đã được duyệt")

    service = models.ForeignKey(
        verbose_name=_("Dịch vụ"),
        to=Service,
        on_delete=models.CASCADE,
    )
    personal_information = models.ForeignKey(
        verbose_name=_("Người sử dụng dịch vụ"),
        to=PersonalInformation,
        on_delete=models.CASCADE,
    )
    resident = models.ForeignKey(
        verbose_name=_("Cư dân đăng ký"), to=get_user_model(), on_delete=models.CASCADE
    )
    status = models.CharField(
        _("Trạng thái"),
        max_length=30,
        choices=Status,
        default=Status.WAITING_FOR_APPROVAL,
    )

    class Meta:
        verbose_name = _("Đăng ký dịch vụ")
        verbose_name_plural = _("Đăng ký dịch vụ")

    def __str__(self) -> str:
        return f"{self.personal_information} {self.service} - {self.get_status_label()}"


class VehicleInformation(MyBaseModel):
    class VehicleType(models.TextChoices):
        BYCYCLE = "BYCYCLE", _("Xe đạp")
        MOTORBIKE = "MOTORBIKE", _("Xe máy")
        CAR = "CAR", _("Xe ô tô")

    license_plate = models.CharField(
        _("Biển số"),
        max_length=10,
        unique=True,
        validators=[MinLengthValidator(6)],
        null=True,
        blank=True,
    )
    vehicle_type = models.CharField(
        _("Loại phương tiện"), max_length=20, choices=VehicleType
    )
    service_registration = models.OneToOneField(
        verbose_name=_("Dịch vụ đăng ký"),
        to=ServiceRegistration,
        on_delete=models.CASCADE,
    )
    apartment = models.ForeignKey(
        verbose_name=_("Căn hộ"), to=Apartment, on_delete=models.CASCADE
    )

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
