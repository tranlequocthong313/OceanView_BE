from typing import Any

from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from app import settings
from app.admin import MyBaseModelAdmin, admin_site
from notification.manager import NotificationManager
from notification.types import EntityType
from user.admin import issue_account
from utils import get_logger

from .models import (
    MyBaseServiceStatus,
    ReissueCard,
    Relative,
    Service,
    ServiceRegistration,
    Vehicle,
)

log = get_logger(__name__)


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


class MyBaseServiceStatusAmin(MyBaseModelAdmin):
    def post_save(self, instance):
        return instance

    def approve(self, request, instance):
        if instance.is_approved:
            log.error("Faild to approve service registration")
            messages.add_message(
                request,
                messages.ERROR,
                "Approve failed. Service registration has been approved already",
            )
            return False
        else:
            success = instance.approve()
            if success:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    "Approved service registration successfully",
                )
                log.info("Service registration is approved")
            self.post_save(instance)
            return success

    def reject(self, request, instance):
        if instance.is_rejected:
            log.error("Faild to reject service registration")
            messages.add_message(
                request,
                messages.ERROR,
                "Reject failed. Service registration has been rejected already",
            )
            return False
        else:
            success = instance.reject()
            if success:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    "Rejected service registration successfully",
                )
                log.info("Service registration is rejected")
            self.post_save(instance)
            return success

    def response_change(self, request, obj):
        if "_approve-service-registration" in request.POST:
            self.approve(request, obj)
            return HttpResponseRedirect(".")
        if "_reject-service-registration" in request.POST:
            self.reject(request, obj)
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)


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


class ServiceRegistrationAdmin(MyBaseServiceStatusAmin):
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
    fields = (
        "service",
        "personal_information",
        "resident",
        "apartment",
        "payment",
        "status",
    )
    exclude = ("deleted",)
    list_filter = ("status", "service__id", "payment")
    change_form_template = "admin/service_registration_change_form.html"
    readonly_fields = (
        "service",
        "personal_information",
        "resident",
        "apartment",
        "status",
    )

    def approve(self, request, instance):
        success = super().approve(request, instance)
        if not success:
            return
        if instance.service.id == Service.ServiceType.RESIDENT_CARD and issue_account(
            request, instance.personal_information
        ):
            instance.personal_information.user.apartment_set.add(instance.apartment_id)

    def post_save(self, instance):
        send_notification(
            instance,
            approved_entity=EntityType.SERVICE_APPROVED,
            rejected_entity=EntityType.SERVICE_REJECTED,
            filters={"resident_id": instance.resident.resident_id},
        )
        return super().post_save(instance)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: Any | None = ...
    ) -> bool:
        return False


class ReissueCardAdmin(MyBaseServiceStatusAmin):
    approved_entity = EntityType.REISSUE_APPROVED
    rejected_entity = EntityType.REISSUE_REJECTED

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
    readonly_fields = ("service_registration", "status")
    change_form_template = "admin/service_registration_change_form.html"

    def post_save(self, instance):
        send_notification(
            instance,
            approved_entity=EntityType.REISSUE_APPROVED,
            rejected_entity=EntityType.REISSUE_REJECTED,
            filters={"resident_id": instance.service_registration.resident.resident_id},
        )
        return super().post_save(instance)

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
admin.site.register(Relative, RelativeAdmin)
