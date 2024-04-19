from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    DateField,
    ForeignKey,
    ManyToManyField,
    SmallIntegerField,
    TextChoices,
)
from django.utils.translation import gettext_lazy as _

from app.models import MyBaseModel


class ApartmentBuilding(MyBaseModel):
    name = CharField(_("Tên chung cư"), max_length=50)
    address = CharField(_("Địa chỉ"), max_length=50)
    owner = CharField(_("Chủ sở hữu"), max_length=50)
    phone_number = CharField(
        _("Số điện thoại"),
        max_length=11,
        validators=[MinLengthValidator(10)],
    )
    built_date = DateField(_("Năm xây dựng"))

    class Meta:
        verbose_name = _("Chung cư")
        verbose_name_plural = _("Chung cư")

    def __str__(self) -> str:
        return self.name


class Building(MyBaseModel):
    name = CharField(_("Tên tòa nhà"), max_length=10, primary_key=True)
    number_of_floors = SmallIntegerField(
        _("Số tầng"), validators=[MinValueValidator(0)]
    )
    apartment_building = ForeignKey(
        verbose_name=_("Chung cư"), to=ApartmentBuilding, on_delete=CASCADE
    )

    class Meta:
        verbose_name = _("Tòa nhà")
        verbose_name_plural = _("Tòa nhà")

    def __str__(self) -> str:
        return self.name


class ApartmentType(MyBaseModel):
    name = CharField(_("Tên loại căn hộ"), max_length=50)
    width = SmallIntegerField(_("Chiều rộng"), validators=[MinValueValidator(0)])
    height = SmallIntegerField(_("Chiều dài"), validators=[MinValueValidator(0)])
    number_of_bedroom = SmallIntegerField(
        _("Số phòng ngủ"), validators=[MinValueValidator(0)]
    )
    number_of_living_room = SmallIntegerField(
        _("Số phòng khách"), validators=[MinValueValidator(0)]
    )
    number_of_kitchen = SmallIntegerField(
        _("Số phòng bếp"), validators=[MinValueValidator(0)]
    )
    number_of_restroom = SmallIntegerField(
        _("Số nhà tắm"), validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = _("Loại căn hộ")
        verbose_name_plural = _("Loại căn hộ")

    def __str__(self) -> str:
        return self.name


class Apartment(MyBaseModel):
    class Status(TextChoices):
        EMPTY = "EMPTY", _("Trống")
        INHABITED = "INHABITED", _("Có người ở")
        ABOUT_TO_MOVE = "ABOUT_TO_MOVE", _("Sắp chuyển đi")

    room_number = CharField(_("Số phòng"), primary_key=True, max_length=20)
    floor = SmallIntegerField(_("Tầng"), validators=[MinValueValidator(0)])
    apartment_type = ForeignKey(
        verbose_name=_("Loại căn hộ"), to=ApartmentType, on_delete=SET_NULL, null=True
    )
    building = ForeignKey(verbose_name=_("Tòa"), to=Building, on_delete=CASCADE)
    residents = ManyToManyField(
        verbose_name=_("Danh sách cư dân"), to=get_user_model(), blank=True
    )
    status = CharField(
        _("Trạng thái"), max_length=20, choices=Status, default=Status.EMPTY
    )

    class Meta:
        verbose_name = _("Căn hộ")
        verbose_name_plural = _("Căn hộ")

    @classmethod
    def generate_room_number(cls, building_name, floor, room_number):
        # Construct room number using building name and floor
        room_number = f"{building_name}-{floor}{int(room_number):02d}"
        return room_number

    def save(self, *args, **kwargs):
        if self.floor > self.building.number_of_floors:
            raise ValueError(
                "appartment's floor must be less than or equal the building's number of floors"
            )
        self.room_number = Apartment.generate_room_number(
            building_name=self.building, floor=self.floor, room_number=self.room_number
        )
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.room_number)
