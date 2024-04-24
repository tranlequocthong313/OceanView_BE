import contextlib
from datetime import datetime

from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from app.models import MyBaseModel

from .managers import CustomUserWithForeignKeyManager


class PersonalInformation(MyBaseModel):
    class Gender(models.TextChoices):
        MALE = "MALE", _("Nam")
        FEMALE = "FEMALE", _("Nữ")

    citizen_id = models.CharField(
        _("Số căn cước công dân"),
        max_length=12,
        validators=[MinLengthValidator(12)],
        primary_key=True,
    )
    full_name = models.CharField(_("Họ tên"), max_length=50)
    date_of_birth = models.DateField(_("Ngày sinh"), null=True, blank=True)
    phone_number = models.CharField(
        _("Số điện thoại"),
        max_length=11,
        unique=True,
        validators=[MinLengthValidator(10)],
    )
    email = models.EmailField(_("Email"), unique=True, null=True, blank=True)
    hometown = models.CharField(_("Quê quán"), max_length=50, null=True, blank=True)
    gender = models.CharField(
        _("Giới tính"), max_length=6, choices=Gender.choices, default=Gender.MALE
    )

    class Meta:
        verbose_name = _("Thông tin cá nhân")
        verbose_name_plural = _("Thông tin cá nhân")

    def has_account(self):
        return hasattr(self, "user") and self.user is not None

    def is_issued(self):
        return self.has_account() and self.user.is_issued

    def is_same_person(self, data):
        return (
            data.get("citizen_id") == self.citizen_id
            or data.get("phone_number") == self.phone_number
            or (self.email is not None and data.get("email") == self.email)
        )

    @property
    def is_relative(self):
        result = False
        with contextlib.suppress(ObjectDoesNotExist):
            result = self.relative is not None
        return result

    def __str__(self) -> str:
        return f"{self.citizen_id} - {self.full_name}"


class User(AbstractBaseUser, PermissionsMixin):
    class Status(models.TextChoices):
        NOT_ISSUED_YET = "NOT_ISSUED_YET", _("Chưa cấp phát")
        ISSUED = "ISSUED", _("Đã cấp phát")
        ACTIVE = "ACTIVE", _("Đã kích hoạt")
        BANNED = "BANNED", _("Bị khóa")

    class LockerStatus(models.TextChoices):
        EMPTY = "EMPTY", _("Trống")
        NOT_EMPTY = "NOT_EMPTY", _("Có đồ")

    resident_id = models.CharField(
        _("Mã số cư dân"),
        max_length=6,
        unique=True,
        primary_key=True,
        validators=[MinLengthValidator(6)],
    )
    personal_information = models.OneToOneField(
        verbose_name=_("Thông tin cá nhân"),
        to=PersonalInformation,
        on_delete=models.CASCADE,
    )
    password = models.CharField(
        _("Mật khẩu"), max_length=128, validators=[MinLengthValidator(8)]
    )
    avatar = CloudinaryField(_("Ảnh đại diện"), null=True, blank=True)
    is_staff = models.BooleanField(_("Là staff"), default=False)
    is_superuser = models.BooleanField(_("Là superuser"), default=False)
    previous_status = models.CharField(
        _("Trạng thái trước khị bị ban"),
        max_length=15,
        choices=Status.choices,
        null=True,
        blank=True,
    )
    status = models.CharField(
        _("Trạng thái"),
        max_length=15,
        choices=Status.choices,
        default=Status.NOT_ISSUED_YET,
    )
    issued_by = models.ForeignKey(
        verbose_name=_("Cấp phát bởi"),
        to="self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "resident_id"
    objects = CustomUserWithForeignKeyManager()
    REQUIRED_FIELDS = ["personal_information_id"]

    class Meta:
        verbose_name = _("Người dùng")
        verbose_name_plural = _("Người dùng")

    """
    Generate a unique resident ID based on the year and a unique number.

    Args:
        year (int): The year to be used in the resident ID generation.
        unique_number (int): The unique number to be included in the resident ID.

    Returns:
        str: The generated resident ID.
    """

    @classmethod
    def __generate_resident_id(cls, year, unique_number):
        return f"{year % 100:02d}{unique_number:04d}"

    @classmethod
    def generate_resident_id(cls):
        current_year = int(datetime.now().year)
        latest_resident = User.objects.order_by("-resident_id").first()
        unique_number = 1
        if latest_resident:
            last_resident_year = int(latest_resident.resident_id[:2])
            if last_resident_year == int(str(current_year)[2:]):
                digits_length = len(latest_resident.resident_id[2:])
                unique_number = int(latest_resident.resident_id[2:]) + 1
                if len(str(unique_number)) > digits_length:
                    raise OverflowError(
                        "surpass the apartment's ability to issue IDs in 1 year"
                    )
            else:
                unique_number = 1
        else:
            unique_number = 1

        return cls.__generate_resident_id(
            year=current_year, unique_number=unique_number
        )

    @classmethod
    def create_user(cls, password=None, **extra_fields):
        user = cls(resident_id=cls.generate_resident_id(), **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def revoke(self):
        self.status = self.Status.NOT_ISSUED_YET
        self.save()
        return True

    def issue(self):
        self.status = self.Status.ISSUED
        self.save()
        return True

    def active(self):
        self.status = self.Status.ACTIVE
        self.save()
        return True

    def ban(self):
        self.previous_status = self.status
        self.status = self.Status.BANNED
        self.save()
        return True

    def unban(self):
        self.status = self.previous_status
        self.save()
        return True

    @property
    def is_issued(self):
        return self.status != self.Status.NOT_ISSUED_YET

    @property
    def is_banned(self):
        return self.status == self.Status.BANNED

    @property
    def is_active_user(self):
        return self.status == self.Status.ACTIVE

    def change_password(self, new_password):
        self.set_password(new_password)
        self.save()

    def is_same_person(self, data):
        return self.personal_information.is_same_person(data)

    def __str__(self) -> str:
        return f"{self.resident_id} - {self.personal_information.full_name}"
