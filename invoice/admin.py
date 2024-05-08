from django.contrib import admin
from django.utils.html import mark_safe
from vnpay.admin import BillingAdmin
from vnpay.models import Billing

from app.admin import MyBaseModelAdmin, admin_site
from utils import format, get_logger

from . import models

log = get_logger(__name__)


class InvoiceAdmin(MyBaseModelAdmin):
    def formatted_amount(self, obj):
        return format.format_currency(obj.total_amount)

    formatted_amount.short_description = "Tổng cộng"

    list_display = (
        "id",
        "formatted_amount",
        "due_date",
        "resident",
    )
    search_fields = (
        "id",
        "resident__pk",
        "resident__personal_information__full_name",
        "resident__personal_information__email",
        "resident__personal_information__phone_number",
    )
    exclude = ("id",)
    exclude = ("deleted",)


class InvoiceDetailAdmin(MyBaseModelAdmin):
    list_display = ("id", "service_registration", "invoice", "amount")
    search_fields = (
        "id",
        "service_registration__service__name",
        "service_registration__service__id",
        "invoice__id",
        "amount",
    )
    list_filter = ("service_registration__service__id",)
    exclude = ("deleted",)


class PaymentAdmin(MyBaseModelAdmin):
    list_display = (
        "id",
        "method",
        "status",
        "invoice",
        "total_amount",
    )
    readonly_fields = (
        "id",
        "method",
        "invoice",
        "total_amount",
    )
    search_fields = (
        "id",
        "method",
        "status",
        "total_amount",
        "invoice__id",
    )
    list_filter = (
        "method",
        "status",
    )
    exclude = ("deleted",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OnlineWalletAdmin(MyBaseModelAdmin):
    list_display = (
        "id",
        "payment",
        "vnpay_billing",
    )
    search_fields = (
        "id",
        "payment__status",
        "vnpay_billing__id",
        "vnpay_billing__transaction_id",
        "vnpay_billing__reference_number",
    )
    list_filter = ("payment__status",)
    exclude = ("deleted",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ProofImageAdmin(MyBaseModelAdmin):
    list_display = (
        "id",
        "payment",
    )
    search_fields = (
        "id",
        "payment__status",
    )
    readonly_fields = ("_image",)
    list_filter = ("payment__status",)
    exclude = ("deleted",)

    @admin.display(description="Ảnh")
    def _image(self, obj):
        return mark_safe(f'<img width="500" src="{obj.image_url}" />')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin_site.register(models.Invoice, InvoiceAdmin)
admin_site.register(models.InvoiceDetail, InvoiceDetailAdmin)
admin_site.register(models.Payment, PaymentAdmin)
admin_site.register(models.ProofImage, ProofImageAdmin)
admin_site.register(models.OnlineWallet, OnlineWalletAdmin)

admin_site.register(Billing, BillingAdmin)
