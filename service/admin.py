import logging

from app.admin import MyBaseModelAdmin, admin_site
from utils import format

from .models import (
    Relative,
    Service,
    ServiceRegistration,
    VehicleInformation,
)

log = logging.getLogger(__name__)


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
        "status",
    )
    search_fields = (
        "id",
        "personal_information__citizen_id",
        "personal_information__full_name",
        "personal_information__phone_number",
        "personal_information__email",
        "resident_id",
        "status",
    )
    list_filter = ("status",)


admin_site.register(Relative)
admin_site.register(VehicleInformation)
admin_site.register(Service, ServiceAdmin)
admin_site.register(ServiceRegistration, ServiceRegistrationAdmin)
