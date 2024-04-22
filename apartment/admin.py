import logging

from app.admin import MyBaseModelAdmin, admin_site

from . import models

log = logging.getLogger(__name__)


class ApartmentBuildingAdmin(MyBaseModelAdmin):
    list_display = ["name", "address", "owner", "phone_number", "built_date"]


class BuildingAdmin(MyBaseModelAdmin):
    list_display = ["name", "number_of_floors", "apartment_building"]


class ApartmentTypeAdmin(MyBaseModelAdmin):
    list_display = [
        "name",
        "width",
        "height",
        "number_of_bedroom",
        "number_of_living_room",
        "number_of_kitchen",
        "number_of_restroom",
    ]


class ApartmentAdmin(MyBaseModelAdmin):
    list_display = ("room_number", "floor", "apartment_type", "building", "status")
    search_fields = (
        "room_number",
        "apartment_type__name",
        "building__name",
        "floor",
        "status",
    )
    list_filter = (
        "building__name",
        "floor",
        "status",
        "apartment_type__name",
    )
    filter_horizontal = ["residents"]


admin_site.register(models.Apartment, ApartmentAdmin)
admin_site.register(models.ApartmentBuilding, ApartmentBuildingAdmin)
admin_site.register(models.ApartmentType, ApartmentTypeAdmin)
admin_site.register(models.Building, BuildingAdmin)
