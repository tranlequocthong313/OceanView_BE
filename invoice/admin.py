from calendar import monthrange
from datetime import datetime
from typing import Any

from django.contrib import admin
from django.db.models import Sum
from django.db.models.base import post_save
from django.dispatch import receiver
from django.http import HttpRequest
from django.utils.html import mark_safe
from vnpay.admin import BillingAdmin
from vnpay.models import Billing

from app import settings
from app.admin import MyBaseModelAdmin, admin_site
from notification.manager import NotificationManager
from notification.types import EntityType
from utils import format, get_logger

from . import models

log = get_logger(__name__)


class InvoiceAdmin(MyBaseModelAdmin):
    def formatted_amount(self, obj):
        return format.format_currency(obj.total_amount)

    formatted_amount.short_description = "Tổng cộng"

    list_display = ("id", "formatted_amount", "due_date", "resident", "status")
    search_fields = (
        "id",
        "resident__pk",
        "resident__personal_information__full_name",
        "resident__personal_information__email",
        "resident__personal_information__phone_number",
        "status",
    )
    list_filter = ("status",)
    exclude = ("deleted", "id")


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
    list_display = ("id", "payment", "reference_number", "transaction_id")
    search_fields = ("id", "payment__status", "reference_number", "transaction_id")
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


class VnPayBillingAdmin(BillingAdmin, MyBaseModelAdmin):
    search_fields = (
        "id",
        "pay_by__resident_id",
        "pay_by__personal_information__full_name",
        "pay_by__personal_information__phone_number",
        "pay_by__personal_information__email",
    )


class StatsRevenueAdmin(admin.ModelAdmin):
    change_list_template = "admin/stats/revenue_change_list.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = "Thống kê doanh thu"
        extra_context["chart_data"] = self.get_revenue_stats()
        return super().changelist_view(request, extra_context=extra_context)

    def get_revenue_stats(self):
        current_year = datetime.now().year
        data = {}

        for month in range(1, 13):
            days_in_month = monthrange(current_year, month)[1]
            start_date = datetime(current_year, month, 1)
            end_date = datetime(current_year, month, days_in_month)

            total_revenue = models.Invoice.objects.filter(
                due_date__gte=start_date, due_date__lte=end_date
            ).aggregate(total_revenue=Sum("total_amount"))["total_revenue"]

            data[f"{month}-{current_year}"] = int(total_revenue) if total_revenue else 0

        return data

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: Any | None = ...
    ) -> bool:
        return False

    def has_change_permission(self, request, obj=None):
        return False


@receiver(post_save, sender=models.Invoice)
def notifiy_to_resident(sender, instance, created, **kwargs):
    if created:
        NotificationManager.create_notification(
            entity=instance,
            entity_type=EntityType.INVOICE_CREATE,
            image=settings.LOGO,
            filters={"resident_id": instance.resident.resident_id},
        )


admin_site.register(models.Invoice, InvoiceAdmin)
admin_site.register(models.InvoiceDetail, InvoiceDetailAdmin)
admin_site.register(models.Payment, PaymentAdmin)
admin_site.register(models.ProofImage, ProofImageAdmin)
admin_site.register(models.OnlineWallet, OnlineWalletAdmin)
admin_site.register(models.StatsRevenue, StatsRevenueAdmin)

admin_site.register(Billing, VnPayBillingAdmin)
