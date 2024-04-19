from datetime import datetime

from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import MinLengthValidator
from django.db.models import (
    CASCADE,
    SET_NULL,
    BooleanField,
    CharField,
    DateField,
    EmailField,
    ForeignKey,
    OneToOneField,
    TextChoices,
)
from django.utils.translation import gettext_lazy as _

from app.models import MyBaseModel

from .managers import CustomUserWithForeignKeyManager


class PersonalInformation(MyBaseModel):
    class Gender(TextChoices):
        MALE = "MALE", _("Nam")
        FEMALE = "FEMALE", _("Nữ")

    citizen_id = CharField(
        _("Số căn cước công dân"),
        max_length=12,
        validators=[MinLengthValidator(12)],
        primary_key=True,
    )
    full_name = CharField(_("Họ tên"), max_length=50)
    date_of_birth = DateField(_("Ngày sinh"), null=True)
    phone_number = CharField(
        _("Số điện thoại"),
        max_length=11,
        unique=True,
        validators=[MinLengthValidator(10)],
    )
    email = EmailField(_("Email"), unique=True, null=True, blank=True)
    hometown = CharField(_("Quê quán"), max_length=50, null=True)
    gender = CharField(
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

    def __str__(self) -> str:
        return f"{self.citizen_id} - {self.full_name}"


class User(AbstractBaseUser, PermissionsMixin):
    class Status(TextChoices):
        NOT_ISSUED_YET = "NOT_ISSUED_YET", _("Chưa cấp phát")
        ISSUED = "ISSUED", _("Đã cấp phát")
        ACTIVE = "ACTIVE", _("Đã kích hoạt")
        BANNED = "BANNED", _("Bị khóa")

    resident_id = CharField(
        _("Mã số cư dân"),
        max_length=6,
        unique=True,
        primary_key=True,
        validators=[MinLengthValidator(6)],
    )
    personal_information = OneToOneField(
        verbose_name=_("Thông tin cá nhân"),
        to=PersonalInformation,
        on_delete=CASCADE,
    )
    password = CharField(
        _("Mật khẩu"), max_length=128, validators=[MinLengthValidator(8)]
    )
    avatar = CloudinaryField(_("Ảnh đại diện"), null=True, blank=True)
    is_staff = BooleanField(_("Là staff"), default=False)
    is_superuser = BooleanField(_("Là superuser"), default=False)
    previous_status = CharField(
        _("Trạng thái trước khị bị ban"),
        max_length=15,
        choices=Status.choices,
        null=True,
        blank=True,
    )
    status = CharField(
        _("Trạng thái"),
        max_length=15,
        choices=Status.choices,
        default=Status.NOT_ISSUED_YET,
    )
    issued_by = ForeignKey(
        verbose_name=_("Cấp phát bởi"),
        to="self",
        on_delete=SET_NULL,
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "resident_id"
    objects = CustomUserWithForeignKeyManager()
    REQUIRED_FIELDS = ["personal_information_id"]

    class Meta:
        verbose_name = _("Người dùng")
        verbose_name_plural = _("Người dùng")

    @classmethod
    def __generate_resident_id(cls, year, unique_number):
        """
        Combine last 2 digits of a year and a unique number
        Ex: Year = 2024, Unique_number = 25
        => Resident Id = 240025
        It can only provide ids for 9999 residents per year for the app context
        """
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
