import logging

from django.apps import apps

from app.admin import MyBaseModelAdmin, admin_site

log = logging.getLogger(__name__)


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


# TODO: Custom Apartment Residents admin model view

model_admins = {
    "apartment": ApartmentAdmin,
}

apartment_app = apps.get_app_config("apartment")

for model_name, model in apartment_app.models.items():
    admin_site.register(model, model_admins.get(model_name))
