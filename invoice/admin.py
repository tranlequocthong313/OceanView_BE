import logging

from django.apps import apps

from app.admin import MyBaseModelAdmin, admin_site
from utils import format

log = logging.getLogger(__name__)


class InvoiceAdmin(MyBaseModelAdmin):
    def formatted_amount(self, obj):
        return format.format_currency(obj.amount)

    formatted_amount.short_description = "Tổng cộng"

    list_display = (
        "id",
        "formatted_amount",
        "due_date",
        "resident",
        "payment_status",
        "invoice_type",
    )
    search_fields = ("id", "payment_status")
    exclude = (
        "id",
        "payment_status",
    )


class InvoiceDetailAdmin(MyBaseModelAdmin):
    list_display = (
        "id",
        "payment_method",
        "transaction_code",
        "payment_proof",
        "invoice",
    )
    search_fields = (
        "id",
        "payment_method",
        "transaction_code",
        "invoice__id",
    )
    list_filter = ("payment_method",)


model_admins = {
    "invoice": InvoiceAdmin,
    "invoicedetail": InvoiceDetailAdmin,
}

apartment_app = apps.get_app_config("invoice")

for model_name, model in apartment_app.models.items():
    admin_site.register(model, model_admins.get(model_name))
