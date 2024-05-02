from typing import Any

from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from app.admin import MyBaseModelAdmin, admin_site
from utils import format

from .models import (
    ReissueCard,
    Relative,
    Service,
    ServiceRegistration,
    Vehicle,
)


class RelativeAdmin(MyBaseModelAdmin):
    list_display = ("id", "relationship", "personal_information")
    search_fields = (
        "id",
        "relationship",
        "personal_information__citizen_id",
        "personal_information__full_name",
        "personal_information__phone_number",
        "personal_information__email",
    )

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(Relative, RelativeAdmin)


class ServiceAdmin(MyBaseModelAdmin):
    def formatted_price(self, obj):
        return format.format_currency(obj.price)

    formatted_price.short_description = "Giá"

    list_display = (
        "service_id",
        "name",
        "formatted_price",
    )
    search_fields = (
        "service_id",
        "name",
    )
    list_filter = ("service_id",)


class ServiceRegistrationAdmin(MyBaseModelAdmin):
    list_display = (
        "id",
        "service",
        "personal_information",
        "resident",
        "apartment",
        "status",
    )
    search_fields = (
        "id",
        "personal_information__citizen_id",
        "personal_information__full_name",
        "personal_information__phone_number",
        "personal_information__email",
        "resident__resident_id",
        "apartment__pk",
        "status",
    )
    exclude = ("deleted",)
    list_filter = ("status",)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: Any | None = ...
    ) -> bool:
        return False


class ReissueCardAdmin(MyBaseModelAdmin):
    list_display = (
        "id",
        "service_registration",
        "status",
    )
    search_fields = (
        "id",
        "service_registration__personal_information__citizen_id",
        "service_registration__personal_information__full_name",
        "service_registration__personal_information__phone_number",
        "service_registration__personal_information__email",
        "service_registration__resident__resident_id",
        "status",
    )
    exclude = ("deleted",)
    list_filter = ("status",)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: Any | None = ...
    ) -> bool:
        return False


class VehicleAdmin(MyBaseModelAdmin):
    list_display = (
        "id",
        "license_plate",
        "vehicle_type",
    )
    search_fields = (
        "license_plate",
        "vehicle_type",
    )
    list_filter = ("vehicle_type",)

    def has_add_permission(self, request, obj=None):
        return False


admin_site.register(Relative, RelativeAdmin)
admin_site.register(Vehicle, VehicleAdmin)
admin_site.register(Service, ServiceAdmin)
admin_site.register(ServiceRegistration, ServiceRegistrationAdmin)
admin_site.register(ReissueCard, ReissueCardAdmin)
