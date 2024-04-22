import logging

from app.admin import MyBaseModelAdmin, admin_site
from utils import format

from . import models

log = logging.getLogger(__name__)


class InvoiceTypeAdmin(MyBaseModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")
    list_filter = ("name",)


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


admin_site.register(models.InvoiceType, InvoiceTypeAdmin)
admin_site.register(models.Invoice, InvoiceAdmin)
admin_site.register(models.InvoiceDetail, InvoiceDetailAdmin)
