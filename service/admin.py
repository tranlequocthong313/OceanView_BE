from typing import Any

from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from app import settings
from app.admin import MyBaseModelAdmin, admin_site
from notification.manager import NotificationManager
from notification.types import EntityType
from user.admin import issue_account

from .models import (
    MyBaseServiceStatus,
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
        "id",
        "name",
        "formatted_price",
    )
    search_fields = (
        "id",
        "name",
    )
    list_filter = ("id",)


def send_notification(obj, approved_entity, rejected_entity, filters):
    if obj.status_changed and obj.status in [
        MyBaseServiceStatus.Status.APPROVED,
        MyBaseServiceStatus.Status.REJECTED,
    ]:
        NotificationManager.create_notification(
            entity=obj,
            entity_type=(approved_entity if obj.is_approved else rejected_entity),
            filters=filters,
            image=settings.LOGO,
        )


class ServiceRegistrationAdmin(MyBaseModelAdmin):
    list_display = (
        "id",
        "service",
        "personal_information",
        "resident",
        "apartment",
        "payment",
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
        "payment",
    )
    exclude = ("deleted",)
    list_filter = ("status", "service__id", "payment")

    def save_model(self, request, obj, form, change):
        send_notification(
            obj=obj,
            approved_entity=EntityType.SERVICE_APPROVED,
            rejected_entity=EntityType.SERVICE_REJECTED,
            filters={"resident_id": obj.resident.resident_id},
        )
        super().save_model(request, obj, form, change)
        if (
            obj.is_approved
            and obj.service.id == Service.ServiceType.RESIDENT_CARD
            and issue_account(request, obj.personal_information)
        ):
            obj.personal_information.user.apartment_set.add(obj.apartment_id)

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

    # TODO: Do this
    def save_model(self, request, obj, form, change):
        send_notification(
            obj=obj,
            approved_entity=EntityType.REISSUE_APPROVED,
            rejected_entity=EntityType.REISSUE_REJECTED,
            filters={"resident_id": obj.service_registration.resident.resident_id},
        )
        super().save_model(request, obj, form, change)

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
