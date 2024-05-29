import contextlib

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apartment.models import Apartment
from app.models import MyBaseModel, MyBaseModelWithDeletedState
from user.models import PersonalInformation


class Service(MyBaseModel):
    class ServiceType(models.TextChoices):
        ACCESS_CARD = "ACCESS_CARD", _("Thẻ ra vào")
        RESIDENT_CARD = "RESIDENT_CARD", _("Thẻ cư dân")
        BICYCLE_PARKING_CARD = "BICYCLE_PARKING_CARD", _("Thẻ gửi xe đạp")
        MOTOR_PARKING_CARD = "MOTOR_PARKING_CARD", _("Thẻ gửi xe máy")
        CAR_PARKING_CARD = "CAR_PARKING_CARD", _("Thẻ gửi xe ô tô")
        MANAGING = "MANAGING", _("Quản lý")

    id = models.CharField(
        verbose_name=_("Mã dịch vụ"),
        primary_key=True,
        max_length=30,
        choices=ServiceType.choices,
    )
    name = models.CharField(verbose_name=_("Tên dịch vụ"), max_length=50)
    price = models.PositiveBigIntegerField(
        _("Giá"),
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = _("Dịch vụ")
        verbose_name_plural = _("Dịch vụ")

    @classmethod
    def monthly_services(cls):
        return cls.parking_services + [
            Service.ServiceType.MANAGING,
        ]

    @classmethod
    def parking_services(cls):
        return [
            Service.ServiceType.BICYCLE_PARKING_CARD,
            Service.ServiceType.MOTOR_PARKING_CARD,
            Service.ServiceType.CAR_PARKING_CARD,
        ]

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


class MyBaseServiceStatus(MyBaseModelWithDeletedState):
    class Status(models.TextChoices):
        WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL", _("Chờ được xét duyệt")
        APPROVED = "APPROVED", _("Đã được duyệt")
        REJECTED = "REJECTED", _("Bị từ chối")
        CANCELED = "CANCELED", _("Đã hủy")

    previous_status = models.CharField(
        _("Trạng thái trước"),
        max_length=30,
        choices=Status,
        default=None,
        null=True,
        blank=True,
    )
    status = models.CharField(
        _("Trạng thái"),
        max_length=30,
        choices=Status,
        default=Status.WAITING_FOR_APPROVAL,
    )
    __prev_status = None

    @property
    def status_changed(self):
        return self.__prev_status != self.status

    @property
    def is_approved(self):
        return self.status == MyBaseServiceStatus.Status.APPROVED

    @property
    def is_rejected(self):
        return self.status == MyBaseServiceStatus.Status.REJECTED

    @property
    def is_canceled(self):
        return self.status == MyBaseServiceStatus.Status.CANCELED

    @property
    def is_waiting_for_approval(self):
        return self.status == MyBaseServiceStatus.Status.WAITING_FOR_APPROVAL

    def approve(self):
        self.previous_status = self.status
        self.__prev_status = self.status
        self.status = MyBaseServiceStatus.Status.APPROVED
        self.save()
        return True

    def reject(self):
        self.previous_status = self.status
        self.__prev_status = self.status
        self.status = MyBaseServiceStatus.Status.REJECTED
        self.save()
        return True

    def cancel(self):
        self.previous_status = self.status
        self.__prev_status = self.status
        self.status = MyBaseServiceStatus.Status.CANCELED
        self.save()
        return True

    class Meta:
        abstract = True


class ServiceRegistration(MyBaseServiceStatus):
    class Payment(models.TextChoices):
        FREE = "FREE", _("Miễn phí")
        DAILY = "DAILY", _("Theo ngày")
        MONTHLY = "MONTHLY", _("Theo tháng")
        IMMEDIATELY = "IMMEDIATELY", _("Ngay lúc đăng ký")

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
    apartment = models.ForeignKey(
        verbose_name=_("Căn hộ"),
        to=Apartment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    payment = models.CharField(
        verbose_name=_("Hình thức thanh toán"),
        choices=Payment.choices,
        max_length=20,
        default=Payment.MONTHLY,
    )

    class Meta:
        verbose_name = _("Đăng ký dịch vụ")
        verbose_name_plural = _("Đăng ký dịch vụ")

    @property
    def has_vehicle(self):
        result = False
        with contextlib.suppress(ObjectDoesNotExist):
            result = self.vehicle is not None
        return result

    @property
    def for_relative(self):
        return self.personal_information.is_relative

    def __str__(self) -> str:
        return f"{self.personal_information} {self.service}"


class Vehicle(MyBaseModel):
    class VehicleType(models.TextChoices):
        BICYCLE = "BICYCLE", _("Xe đạp")
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

    class Meta:
        verbose_name = _("Phương tiện")
        verbose_name_plural = _("Phương tiện")

    @classmethod
    def get_vehicle_type_label(cls, vehicle_type):
        return dict(cls.VehicleType.choices)[vehicle_type]

    def __str__(self) -> str:
        return f"{Vehicle.get_vehicle_type_label(self.vehicle_type)} - {self.license_plate or ''}"

    @classmethod
    def get_service_id(cls, vehicle_type):
        idS = {
            cls.VehicleType.BICYCLE: Service.ServiceType.BICYCLE_PARKING_CARD,
            cls.VehicleType.MOTORBIKE: Service.ServiceType.MOTOR_PARKING_CARD,
            cls.VehicleType.CAR: Service.ServiceType.CAR_PARKING_CARD,
        }
        return idS[vehicle_type]


class ReissueCard(MyBaseServiceStatus):
    service_registration = models.ForeignKey(
        verbose_name=_("Đăng ký dịch vụ"),
        to=ServiceRegistration,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Cấp  lại thẻ")
        verbose_name_plural = _("Cấp  lại thẻ")

    def __str__(self) -> str:
        return self.service_registration.__str__()
